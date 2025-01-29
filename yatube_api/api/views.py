from rest_framework import viewsets, status, permissions
from posts.models import Post, Comment, Group, Follow, User
from rest_framework.exceptions import (PermissionDenied, NotFound,
                                       ValidationError)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (PostSerializer, CommentSerializer,
                          GroupSerializer,
                          FollowSerializer)


class PostsViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Получаем публикацию по id

        if instance.author != request.user:
            raise PermissionDenied("У вас недостаточно прав для "
                                   "выполнения данного действия.")

        # Если пользователь является автором, выполняем обновление
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # Получаем публикацию по id

        # Проверяем, что текущий пользователь является автором публикации
        if instance.author != request.user:
            raise PermissionDenied("У вас недостаточно прав для выполнения"
                                   " данного действия.")

        # Если пользователь является автором, выполняем удаление
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Запрет анонимных запросов

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def list(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Публикация не найдена.")

        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def retrieve(self, request, post_id=None, id=None):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Публикация не найдена.")

        try:
            comment = Comment.objects.get(id=id, post=post)
        except Comment.DoesNotExist:
            raise NotFound("Комментарий не найден.")

        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def create(self, request, post_id=None):
        # Проверяем, существует ли публикация с указанным post_id
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Публикация не найдена.")

        # Проверяем, что поле text присутствует в запросе
        if 'text' not in request.data or not request.data['text'].strip():
            raise ValidationError({"text": ["Обязательное поле."]})

        # Создаем комментарий
        comment = Comment.objects.create(
            author=request.user,
            post=post,
            text=request.data['text']
        )

        # Сериализуем и возвращаем созданный комментарий
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, post_id=None, id=None):
        # Проверяем, существует ли публикация с указанным post_id
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Публикация не найдена.")

        try:
            comment = Comment.objects.get(id=id, post=post)
        except Comment.DoesNotExist:
            raise NotFound("Комментарий не найден.")

        # Проверяем, что текущий пользователь является автором комментария
        if comment.author != request.user:
            raise PermissionDenied("У вас недостаточно прав для выполнения "
                                   "данного действия.")

        # Проверяем, что поле text присутствует в запросе и является строкой
        if ('text' not in request.data
                or not isinstance(request.data['text'], str)
                or not request.data['text'].strip()):
            raise ValidationError({"text": ["Обязательное поле."]})

        # Обновляем комментарий
        comment.text = request.data['text']
        comment.save()

        # Сериализуем и возвращаем обновленный комментарий
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def partial_update(self, request, post_id=None, id=None):
        # Проверяем, существует ли публикация с указанным post_id
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Публикация не найдена.")

        try:
            comment = Comment.objects.get(id=id, post=post)
        except Comment.DoesNotExist:
            raise NotFound("Комментарий не найден.")

        # Проверяем, что текущий пользователь является автором комментария
        if comment.author != request.user:
            raise PermissionDenied("У вас недостаточно прав для выполнения"
                                   " данного действия.")

        # Частичное обновление комментария
        serializer = CommentSerializer(comment, data=request.data,
                                       partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Возвращаем обновленный комментарий
        return Response(serializer.data)

    def destroy(self, request, post_id=None, id=None):
        # Проверяем, существует ли публикация с указанным post_id
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Публикация не найдена.")

        try:
            comment = Comment.objects.get(id=id, post=post)
        except Comment.DoesNotExist:
            raise NotFound("Комментарий не найден.")

        # Проверяем, что текущий пользователь является автором комментария
        if comment.author != request.user:
            raise PermissionDenied("У вас недостаточно прав для выполнения"
                                   " данного действия.")

        # Удаляем комментарий
        comment.delete()

        # Возвращаем успешный ответ без содержимого
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Получаем параметр search из запроса
        search_query = request.query_params.get('search', None)

        # Получаем все подписки текущего пользователя
        follows = Follow.objects.filter(user=request.user)

        # Если передан параметр search, фильтруем подписки
        if search_query:
            follows = follows.filter(
                following__username__icontains=search_query
            )

        serializer = FollowSerializer(follows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        following_username = request.data.get('following')
        if not following_username:
            return Response(
                {"error": "Field 'following' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, что пользователь не пытается подписаться на самого себя
        if following_username == request.user.username:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            following_user = User.objects.get(username=following_username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        follow, created = Follow.objects.get_or_create(
            user=request.user,
            following=following_user
        )
        if not created:
            return Response(
                {"error": "Already following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
