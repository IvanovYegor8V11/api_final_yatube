from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    PostViewSet, CommentViewSet, GroupViewSet, FollowViewSet
)

router = SimpleRouter()
router.register('posts', PostViewSet, basename='post')
router.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet,
                basename='comment')
router.register('groups', GroupViewSet, basename='group')
router.register('follow', FollowViewSet, basename='follow')

urlpatterns = [
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(router.urls)),
]
