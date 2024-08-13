from django.urls import path
from .views import (
    register,
    login,
    logout,
    all_post,
    create_post,
    create_like,
    create_comment,
    follow,
    remove_follower,
    create_follow,
    delete_user,
    delete_post,
    remove_like,
    remove_comment,
)
urlpatterns = [
    path('register/',register,name='user-Register'),
    path('deleteuser/<id>/',delete_user,name='delete-user'),
    path('login/',login,name='user-login'),
    path('logout/',logout,name='user-logout'),
    path('allpost/',all_post,name='all-post'),
    path('deletepost/<id>/',delete_post,name='delete-post'),
    path('createpost/',create_post,name='create-post'),
    path('createlike/<id>/',create_like,name='create-like'),
    path('removelike/<id>/',remove_like,name='remove-like'),
    path('createcomment/<id>/',create_comment,name='create-like'),
    path('removecomment/<id>/',remove_comment,name='remove-comment'),
    path('follow/',follow,name='follow'),
    path('createfollow/<id>/',create_follow,name='create-follow'),
    path('removefollower/<id>/',remove_follower,name='remove-follower'),

]