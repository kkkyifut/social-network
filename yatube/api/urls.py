from django.urls import include, path
from django.views.generic import TemplateView

from rest_framework import routers
from rest_framework.authtoken import views

from .views import (CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet,
                    UserViewSet)

app_name = 'api-v1'

router = routers.DefaultRouter()
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'users', UserViewSet, basename='users')
router.register(r'posts/(?P<post_id>\d+)/comments',
                CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/api-token-auth/', views.obtain_auth_token),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('redoc/', TemplateView.as_view(template_name='api/redoc.html'),
         name='redoc'),
]
