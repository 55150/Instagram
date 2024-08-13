from rest_framework import serializers
from .models import (
    User,
    Photo,
    PhotoTag,
    Tag,
    Comment,
    Like,
    Follow,
    UserProfile,
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'created_at']

class PhotoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True)

    class Meta:
        model = Photo
        fields = ['id', 'image_url', 'user', 'tags', 'created_at']
class PhotoTagSerializer(serializers.ModelSerializer):
    model = PhotoTag
    fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag_name', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comment_text', 'photo', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'photo', 'created_at']

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followee', 'created_at']
        # fields = ('follower_id', 'follower__username')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'last_name', 'first_name', 'age']
