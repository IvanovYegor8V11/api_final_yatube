import rest_framework.serializers as slz
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Group, Post, Comment, Follow, User


class GroupSerializer(slz.ModelSerializer):
    """Сериализатор модели Group."""

    class Meta:
        model = Group
        fields = '__all__'


class PostSerializer(slz.ModelSerializer):
    """Сериализатор модели Post."""

    author = slz.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(slz.ModelSerializer):
    """Сериализатор модели Comment."""

    author = slz.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('post',)


class FollowSerializer(slz.ModelSerializer):
    """Сериализатор модели Follow."""

    user = slz.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=slz.CurrentUserDefault(),
    )
    following = slz.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('following', 'user'),
                message='Подписка уже оформлена.',
            )
        ]

    def validate(self, attrs):
        if self.context['request'].user == attrs['following']:
            raise slz.ValidationError('Невозможно подписаться на себя.')
        return attrs
