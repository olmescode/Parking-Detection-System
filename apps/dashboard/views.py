from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.parking.models import Camera, ParkingSpace
import cv2
import json
import base64
import numpy as np
from pathlib import Path
from django.conf import settings

@login_required
def dashboard_view(request):
    cameras = Camera.objects.filter(is_active=True)
    camera_id = request.GET.get('camera')
    
    if camera_id:
        current_camera = cameras.filter(id=camera_id).first()
    else:
        current_camera = cameras.first()
    
    camera_index = 0
    if current_camera:
        camera_list = list(cameras)
        if current_camera in camera_list:
            camera_index = camera_list.index(current_camera)
    
    context = {
        'current_camera': current_camera,
        'cameras': cameras,
        'current_camera_index': camera_index,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def camera_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Nueva Cámara')
        camera_type = request.POST.get('type', 'video')
        url = request.POST.get('url', '')
        
        if camera_type == 'video':
            url = 'demo.mp4'
        elif camera_type == 'usb':
            url = '0'
        
        camera = Camera.objects.create(name=name, type=camera_type, url=url, is_active=False)
        return JsonResponse({'camera_id': camera.id})
    
    return redirect('dashboard')

@login_required
def calibrate_view(request, camera_id):
    camera = Camera.objects.get(id=camera_id)
    context = {'camera': camera}
    return render(request, 'dashboard/calibrate.html', context)

@login_required
@require_POST
def calibrate_save(request, camera_id):
    try:
        data = json.loads(request.body)
        camera = Camera.objects.get(id=camera_id)
        spaces = data.get('spaces', [])
        reference_data = data.get('reference_frame', '')
        
        ParkingSpace.objects.filter(camera=camera).delete()
        
        for space in spaces:
            ParkingSpace.objects.create(
                camera=camera,
                number=space['number'],
                x=space['x'],
                y=space['y'],
                width=space['w'],
                height=space['h']
            )
        
        if reference_data:
            header, encoded = reference_data.split(',', 1)
            image_data = base64.b64decode(encoded)
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            media_dir = Path(settings.MEDIA_ROOT) / 'references'
            media_dir.mkdir(parents=True, exist_ok=True)
            ref_path = media_dir / f'camera_{camera.id}.jpg'
            cv2.imwrite(str(ref_path), img)
            
            camera.reference_image = f'references/camera_{camera.id}.jpg'
        
        camera.is_active = True
        camera.save()
        
        from apps.detection.views import detectors
        if camera_id in detectors:
            del detectors[camera_id]
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def settings_view(request):
    return redirect('dashboard')

@login_required
def camera_delete_view(request, camera_id):
    from apps.detection.views import detectors
    import os
    
    if camera_id in detectors:
        del detectors[camera_id]
    
    try:
        camera = Camera.objects.get(id=camera_id)
        if camera.reference_image and os.path.exists(camera.reference_image.path):
            os.remove(camera.reference_image.path)
        camera.delete()
    except Camera.DoesNotExist:
        pass
    
    return redirect('dashboard')
