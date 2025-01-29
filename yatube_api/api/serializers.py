from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from posts.models import Post, Comment, Group, Follow, User
from rest_framework.validators import UniqueTogetherValidator


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    post = serializers.ReadOnlyField(
        read_only=True, source='post.pk'
    )

    class Meta:
        fields = '__all__'
        model = Comment


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'following',)
        model = Follow

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                "Подписка запрещена"
            )
        return data

    validators = [
        UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('user', 'following')
        )
    ]
