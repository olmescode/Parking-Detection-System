from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('camera/create/', views.camera_create_view, name='camera_create'),
    path('camera/<int:camera_id>/calibrate/', views.calibrate_view, name='calibrate'),
    path('camera/<int:camera_id>/calibrate/save/', views.calibrate_save, name='calibrate_save'),
    path('camera/<int:camera_id>/delete/', views.camera_delete_view, name='camera_delete'),
    path('settings/', views.settings_view, name='settings'),
]
