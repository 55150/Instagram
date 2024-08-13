from django.shortcuts import render,redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from datetime import datetime,timedelta
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db.models import Count
from .models import (
    UserProfile,
    Like,
    Comment,
    Tag,
    PhotoTag,
    Photo,
    Follow,
)
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    LikeSerializer,
    CommentSerializer,
    TagSerializer,
    PhotoTagSerializer,
    PhotoSerializer,
    FollowSerializer
)
# Create your views here.
@api_view(['POST'])
def register(request):
    if request.method == "POST":
        username = request.data.get('username')
        first_name= request.data.get('first_name')
        last_name = request.data.get('last_name')
        age = request.data.get('age')
        email = request.data.get('email')
        mobile_no = request.data.get('mobile_no')
        password = request.data.get('password')
        user_instance = User.objects.create(
            username=username,
            email=email,
            first_name = first_name,
            last_name = last_name,
            )
        user_instance.set_password(password)
        user_instance.save()
        queryset = UserProfile.objects.create(
            user=user_instance,
            first_name = first_name,
            last_name = last_name,
            age = age,
            email = email,
            mobile_no = mobile_no
        )
        queryset.save()
        return Response(
            {'Messege':'Successfull Create User'}
        )
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        print('username',username,password)
        # Check if both username and password are provided
        if not username or not password:
            return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        print('auth',authenticate(username=username, password=password))
        # Check if authentication was successful
        if user is not None:
            print('here')
            # Authentication successful, generate token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': username}, status=status.HTTP_200_OK)
        else:
            # Authentication failed, return error response
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def all_post(request):
    user = request.user
    
    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 2  # Number of posts per page
    
    if request.method == 'GET':
        posts = Photo.objects.all().order_by('-created_at')
        
        # Paginate queryset
        result_page = paginator.paginate_queryset(posts, request)
        
        post_list = []
        for post in result_page:
            tags = [photo_tag.tag.tag_name for photo_tag in post.tags.all()]
            comments = [{'text': comment.comment_text, 'created_at': comment.created_at} for comment in post.comments.all()]
            likes = [like.user.username for like in post.likes.all()]
            likes_count = post.likes.count() 
            comments_count = post.comments.count()

            post_data = {
                'Username': post.user.username,
                'Photo': str(post.Image_url),
                'Tags': tags,
                'Total_comments' :comments_count,
                'Comments': comments,
                'Total_likes':likes_count,
                'Likes': likes
            }
            post_list.append(post_data)

        response_data = {
            'message': f'Welcome, {user.username}!',
            'posts': post_list,
        }
        return paginator.get_paginated_response(response_data)

    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_post(request):
    user = request.user
    if request.method == 'POST':
        Image_url = request.FILES.get('Image_url')
        tag_names = request.data.get('tag_names', [])  # Providing a default value of an empty list if 'tag_names' is not provided
        if not Image_url:
            return Response({'error': 'Please provide an image URL.'}, status=status.HTTP_400_BAD_REQUEST)
        if not tag_names:
            return Response({'error': 'Please provide at least one tag name.'}, status=status.HTTP_400_BAD_REQUEST)
        # Create photo instance
        photo = Photo.objects.create(
            Image_url=Image_url,
            user=user
        )
        tag = Tag.objects.create(
            tag_name=tag_names
            )
        photo_tag = PhotoTag.objects.create(
            photo=photo,
            tag=tag
            )
        response_data = {
            'message': 'Post created successfully.',
            'photo_id': photo.id,
        }
        return Response(response_data)

    return Response({'error': 'Invalid request method.'})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_like(request,id):
    user = request.user
    photos = Photo.objects.get(id=id)
    if request.method == "POST":
        likes = Like.objects.create(
            user = user,
            photo = photos
        )

        response_data = {
                'message': f'You Have Like On  {user.username} Photo',
            }
        return Response(response_data)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_comment(request,id):
    user = request.user
    photos = Photo.objects.get(id=id)
    if request.method == "POST":
        comment_text = request.data.get('comment_text')
        commnets = Comment.objects.create(
            photo = photos,
            comment_text=comment_text

        )

        response_data = {
                'message': f'You Have Comment On  {user.username} Photo',
            }
        return Response(response_data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def follow(request):
    user = request.user
    if request.method == "GET":
        follower_count = Follow.objects.filter(followee_id=user.id).count()
        followers = Follow.objects.filter(followee_id=user.id).values('follower_id', 'follower__username')

        following_count = Follow.objects.filter(follower_id=user.id).count()
        following = Follow.objects.filter(follower_id=user.id).values('followee_id', 'followee__username')
        response_data = {
            'Username': user.username,
            'Followers': follower_count,
            'Following': following_count,
            'Follower User':list(followers),
            'Following USer':list(following)

        }
        return Response(response_data)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_follow(request,id):
    user = request.user
    if request.method == "POST":
        follow = Follow.objects.create(
            followee_id = id,
            follower_id = user.id
        )
        return Response({'messege':'Follow Sucessfull'})
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_follower(request,id):
    user = request.user
    if request.method == "DELETE":
        removeFollow = Follow.objects.filter(followee_id = id).delete()
        return Response({'messege':'You Have Remove Followers Sucessfully'})

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
def delete_user(request,id):
    if request.method == 'DELETE':
        DeleteUser = User.objects.filter(id=id).delete()
        response_data = {
            'messege':'You Have User Delete Successfully '
        }
        return Response(response_data)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_post(request,id):
    user = request.user
    if request.method == 'DELETE':
        Deletepost = Photo.objects.filter(
            user_id=user.id,
            id=id
            ).delete()
        response_data = {
            'messege':'You Have Delete Post Successfully '
        }
        return Response(response_data)
    
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_like(request,id):
    user = request.user
    if request.method == 'DELETE':
        Deletelike = Like.objects.filter(
            user_id=user.id,
            photo_id=id
            ).delete()
        response_data = {
            'messege':'You Have Remove Like Successfully '
        }
        return Response(response_data)
    else:
        response_data = {
            'messege':'Delete Method Allow '
        }
        return Response(response_data)
    
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_comment(request,id):
    user = request.user
    if request.method == 'DELETE':
        Deletecomment = Comment.objects.filter(
            user_id=user.id,
            photo_id=id
            ).delete()
        response_data = {
            'messege':'You Have Remove comment Successfully '
        }
        return Response(response_data)
    else:
        response_data = {
            'messege':'Delete method allow '
        }
        return Response(response_data)