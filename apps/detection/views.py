from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
import cv2
from apps.parking.models import Camera
from apps.detection.detector import ParkingDetector

detectors = {}
latest_results = {}

def cleanup_detector(camera_id):
    if camera_id in detectors:
        try:
            detectors[camera_id].release()
        except:
            pass
        del detectors[camera_id]
    if camera_id in latest_results:
        del latest_results[camera_id]

def get_detector(camera_id):
    cleanup_detector(camera_id)
    
    camera = Camera.objects.get(id=camera_id)
    spaces = [{
        'number': s.number,
        'x': s.x,
        'y': s.y,
        'w': s.width,
        'h': s.height
    } for s in camera.spaces.all()]
    
    reference_path = camera.reference_image.path if camera.reference_image else None
    
    source = camera.url
    if camera.type == 'usb':
        source = int(source) if source else 0
    elif camera.type == 'video':
        source = camera.url if camera.url else 'demo.mp4'
    
    detectors[camera_id] = ParkingDetector(
        source=source,
        spaces=spaces,
        reference_path=reference_path
    )
    
    return detectors[camera_id]

def generate_frames(camera_id):
    detector = None
    try:
        detector = get_detector(camera_id)
        while True:
            result = detector.process_frame()
            if result is None:
                break
            output, results = result
            latest_results[camera_id] = results
            ret, buffer = cv2.imencode('.jpg', output, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except GeneratorExit:
        pass
    except Exception as e:
        print(f"Error in generate_frames: {e}")
    finally:
        cleanup_detector(camera_id)

def camera_feed(request, camera_id):
    return StreamingHttpResponse(
        generate_frames(camera_id),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def get_spaces_status(request, camera_id):
    if camera_id in latest_results:
        return JsonResponse({'spaces': latest_results[camera_id]})
    return JsonResponse({'spaces': []})
