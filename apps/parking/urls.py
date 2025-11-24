from django.urls import path
from apps.detection import views

urlpatterns = [
    path('camera/<int:camera_id>/', views.camera_feed, name='camera_feed'),
]
