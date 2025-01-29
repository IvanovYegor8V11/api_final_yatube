from django.shortcuts import get_object_or_404
from rest_framework import mixins, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from posts.models import Post, Group
from .permissions import GroupOnlyGet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer,
    FollowSerializer)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (GroupOnlyGet,)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.all()

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        instance = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=instance)


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.following.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
