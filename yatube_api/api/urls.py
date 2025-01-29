from django.urls import path, include
from rest_framework import routers

import api.views as vs

router = routers.DefaultRouter()
router.register(
    'groups',
    vs.GroupViewSet,
    basename='groups',
)
router.register(
    'posts',
    vs.PostViewSet,
    basename='posts',
)
router.register(
    r'posts/(?P<post_id>\d+)/comments',
    vs.CommentViewSet,
    basename='comments',
)
router.register(
    'follow',
    vs.FollowViewSet,
    basename='follow',
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls.jwt')),
]
