from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='followers',
                             on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='following',
                                  on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'following')


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name="Название группы")
    slug = models.SlugField(unique=True,
                            verbose_name="Уникальный идентификатор")
    description = models.TextField(verbose_name="Описание группы")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(
        upload_to='posts/', null=True, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, related_name='posts',
        null=True, blank=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True, db_index=True)
