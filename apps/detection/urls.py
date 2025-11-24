from django.urls import path
from . import views

urlpatterns = [
    path('spaces-status/<int:camera_id>/', views.get_spaces_status, name='spaces_status'),
]
