from django.db import models

class Camera(models.Model):
    CAMERA_TYPES = [
        ('video', 'Video'),
        ('usb', 'Cámara USB'),
        ('ip', 'Cámara IP'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CAMERA_TYPES, default='video')
    url = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    reference_image = models.ImageField(upload_to='references/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ParkingSpace(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='spaces')
    number = models.IntegerField()
    is_occupied = models.BooleanField(default=False)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=100)
    height = models.IntegerField(default=100)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['number']
        unique_together = ['camera', 'number']

    def __str__(self):
        return f"Slot {self.number} - Camera {self.camera.name}"

class Config(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key
