from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('new/', views.new_post, name='new'),
    path('follow/', views.follow_index, name='follow_index'),
    path('<str:username>/follow/', views.profile_follow,
         name='profile_follow'),
    path('<str:username>/unfollow/', views.profile_unfollow,
         name='profile_unfollow'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/send_message/', views.send_message,
         name='send_message'),
    path('<str:username>/messages/', views.messages, name='messages'),
    path('<str:username>/<int:post_id>/', views.post_view,
         name='post'),
    path('<str:username>/<int:post_id>/delete/',
         views.delete_post, name='delete_post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit, name='edit'),
    path('<str:username>/<int:post_id>/comments/<int:comment_id>/delete/',
         views.delete_comment, name='delete_comment'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('', views.index, name='index'),
]
