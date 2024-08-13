from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
import mimetypes
from django.contrib.auth.models import User


def validate_file_extension(value):
    allowed_extensions = ['image/jpeg', 'image/png', 'video/mp4', 'video/quicktime']  # Add more video types if necessary
    file_mime_type, _ = mimetypes.guess_type(value.name)
    if file_mime_type not in allowed_extensions:
        raise ValidationError("Unsupported file type. Please upload an image (JPEG, PNG) or a video (MP4, QuickTime).")

class Photo(models.Model):
    Image_url = models.FileField(upload_to='photos/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.user.username)
    

class Tag(models.Model):
    tag_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.tag_name
    

class PhotoTag(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.tag)
    

class Comment(models.Model):
    comment_text = models.TextField()
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True ,null = True, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.comment_text
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.photo.id} , {self.photo.Image_url}-{self.user.username} - "
    class Meta:
        # Ensure each (user, photo) pair is unique
        constraints = [
            models.UniqueConstraint(fields=['user', 'photo'], name='unique_like')
        ]
    

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followee = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.follower.username
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'followee'],
                name='unique_follow_relation'  # You can choose any name for the constraint
            )
        ]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    mobile_no = models.IntegerField()
    def clean(self):
        if self.age < 18:
            raise ValidationError(_('You must be at least 18 years old to register.'))
    def save(self, *args, **kwargs):
        # Check if the email already exists
        existing_user_profile = UserProfile.objects.filter(email=self.email).exclude(user=self.user)
        if existing_user_profile.exists():
            raise ValidationError(_('A user with this email already exists.'))

        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.user.username} - {self.first_name}"