from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Post, Comment, Like

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
         model = User
         fields = ['email', 'phone_number','first_name', 'last_name',
                   'instagram_link', 'reddit_link', 'x_link', 'linkedin_link',
                   'categories', 'password']
         
    def create(self, validated_data):
         password = validated_data.pop('password')
         user = User.objects.create_user(**validated_data)
         user.set_password(password)
         user.save()
         return user
    
class UserProfileSerializer(serializers.ModelSerializer):
     class Meta:
          model = User
          fields = ['id', 'username', 'email', 'first_name', 'last_name', 'instagram_link', 'reddit_link', 'x_link', 'linkedin_link', 'profile_picture', 'categories']
          read_only_fields = ['username']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    commentator_name = serializers.CharField(source='commentator.username', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'commentator', 'commentator_name', 
                 'like_count', 'share_count', 'created_at', 'parent', 'replies']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
