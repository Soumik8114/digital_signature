from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os

class UploadedFile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='uploads/')
    upload_date = models.DateTimeField(default=timezone.now)
    signature = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return os.path.basename(self.uploaded_file.name)

class UserKeyPair(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.TextField()
    private_key_encrypted = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Key pair for {self.user.username}"