import cv2
import numpy as np
from pathlib import Path
from django.conf import settings
import threading

class ParkingDetector:
    def __init__(self, source, spaces=None, reference_path=None):
        self.source = source
        self.spaces = spaces or []
        self.reference_frame = None
        self.reference_size = None
        self.cap = None
        self.is_video = False
        self.last_frame = None
        self.frame_failures = 0
        self.max_failures = 5
        self.lock = threading.Lock()
        
        if isinstance(source, str):
            if source.endswith(('.mp4', '.avi', '.mov')):
                video_path = Path(settings.MEDIA_ROOT) / source
                if not video_path.exists():
                    video_path = Path(settings.BASE_DIR) / source
                self.source = str(video_path)
                self.is_video = True
            elif source.isdigit():
                self.source = int(source)
        
        if reference_path:
            self.load_reference(reference_path)
        
        self._init_capture()
    
    def _init_capture(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except:
                pass
        
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.is_video:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la fuente de video: {self.source}")
        
        self.frame_failures = 0
            
    def load_reference(self, path):
        img = cv2.imread(path)
        if img is not None:
            self.reference_size = (img.shape[1], img.shape[0])
            self.reference_frame = self.preprocess(img)
            
    def preprocess(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        return blur
        
    def check_space(self, frame, space):
        x, y, w, h = space['x'], space['y'], space['w'], space['h']
        
        if y+h > frame.shape[0] or x+w > frame.shape[1]:
            return False
            
        roi = frame[y:y+h, x:x+w]
        
        if self.reference_frame is not None:
            if y+h > self.reference_frame.shape[0] or x+w > self.reference_frame.shape[1]:
                return False
                
            ref_roi = self.reference_frame[y:y+h, x:x+w]
            
            if roi.shape != ref_roi.shape:
                return False
                
            diff = cv2.absdiff(roi, ref_roi)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            non_zero = cv2.countNonZero(thresh)
            total = w * h
            return (non_zero / total) > 0.15
        return False
        
    def detect(self, frame):
        processed = self.preprocess(frame)
        results = []
        
        for space in self.spaces:
            occupied = self.check_space(processed, space)
            results.append({
                'number': space['number'],
                'occupied': occupied,
                'x': space['x'],
                'y': space['y'],
                'w': space['w'],
                'h': space['h']
            })
        return results
        
    def draw_results(self, frame, results):
        output = frame.copy()
        
        for result in results:
            x, y, w, h = result['x'], result['y'], result['w'], result['h']
            color = (0, 0, 255) if result['occupied'] else (0, 255, 0)
            status = "OCUPADO" if result['occupied'] else "LIBRE"
            
            cv2.rectangle(output, (x, y), (x+w, y+h), color, 2)
            cv2.putText(output, f"{result['number']}", (x + 5, y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(output, status, (x + 5, y + 45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        free_count = sum(1 for r in results if not r['occupied'])
        total = len(results)
        cv2.putText(output, f"Libres: {free_count}/{total}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return output
        
    def process_frame(self):
        with self.lock:
            try:
                if self.cap is None or not self.cap.isOpened():
                    self._init_capture()
                
                ret, frame = self.cap.read()
                
                if not ret:
                    self.frame_failures += 1
                    
                    if self.is_video:
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.cap.read()
                    
                    if not ret:
                        if self.frame_failures >= self.max_failures:
                            self._init_capture()
                            ret, frame = self.cap.read()
                        
                        if not ret:
                            if self.last_frame is not None:
                                frame = self.last_frame.copy()
                            else:
                                return None
                else:
                    self.frame_failures = 0
                    self.last_frame = frame.copy()
                
                if self.reference_size is not None:
                    current_size = (frame.shape[1], frame.shape[0])
                    if current_size != self.reference_size:
                        frame = cv2.resize(frame, self.reference_size, interpolation=cv2.INTER_AREA)
                
                if not self.spaces:
                    return frame, []
                    
                results = self.detect(frame)
                output = self.draw_results(frame, results)
                return output, results
                
            except Exception:
                self.frame_failures += 1
                if self.frame_failures >= self.max_failures:
                    try:
                        self._init_capture()
                    except:
                        pass
                
                if self.last_frame is not None:
                    if not self.spaces:
                        return self.last_frame, []
                    results = self.detect(self.preprocess(self.last_frame))
                    output = self.draw_results(self.last_frame, results)
                    return output, results
                
                return None
        
    def release(self):
        with self.lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                finally:
                    self.cap = None
