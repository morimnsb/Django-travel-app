# backend/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    posts = models.ManyToManyField('Post', related_name='authors')
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    place = models.CharField(max_length=255)
    description = models.TextField()
    writer = models.CharField(max_length=255, blank=True, null=True)
    writer_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    images = models.ManyToManyField('Image', through='PostImage', related_name='posts', blank=True)

    ratings = models.JSONField(default=list)
    comments = models.ManyToManyField('Comment', related_name='post_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    writer = models.CharField(max_length=255, blank=True, null=True)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name='post_comments', on_delete=models.CASCADE)
    replies = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f'Comment by {self.writer} on {self.post.title}'

class Reply(models.Model):
    writer = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='replies')
    created_at = models.DateTimeField(default=timezone.now)
    nested_replies = models.ManyToManyField('self', symmetrical=False, related_name='reply_nested_replies', blank=True)
    comment = models.ForeignKey(Comment, related_name='comment_replies', on_delete=models.CASCADE)
    reply_text = models.TextField()

    def __str__(self):
        return f'Reply by {self.writer} on {self.created_at}'

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images')
    image = models.TextField()  

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images_through')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='post_images_through')
