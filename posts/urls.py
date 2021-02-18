from django.urls import path

from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='index'),
    path('group/<slug:slug>/', views.GroupView.as_view(), name='group'),
    path('new/', views.CreatePost.as_view(), name='new_post'),
    path('follow/', views.FollowList.as_view(), name='follow_index'),
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('<str:username>/<int:post_id>/',
         views.PostView.as_view(), name='post'),
    path('<str:username>/<int:post_id>/edit/',
         views.PostUpdate.as_view(), name='post_edit'),
    path('<str:username>/<int:post_id>/comment/',
         views.CommentCreate.as_view(), name='add_comment'),
    path('<str:username>/follow/',
         views.FollowCreate.as_view(), name='profile_follow'),
    path('<str:username>/unfollow/',
         views.FollowDelete.as_view(), name='profile_unfollow'),
]
