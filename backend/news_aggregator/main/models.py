from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    instagram_link = models.URLField(blank=True, null=True)
    reddit_link = models.URLField(blank=True, null = True)
    x_link = models.URLField(blank=True, null = True)
    linkedin_link = models.URLField(blank=True, null = True)
    categories = models.JSONField(default=list, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"{self.first_name}{self.last_name}{self.phone_number}"
        super().save(*args,**kwargs)

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    original_url = models.URLField()
    image_url = models.URLField(blank=True, null=True)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    category = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    commentator = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = [['user', 'post'], ['user', 'comment']]


