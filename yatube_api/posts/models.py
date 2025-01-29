from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

TEXT_LEN = 50


class Group(models.Model):
    """Сообщество.

    Атрибуты:
        - title (CharField): Название сообщества.
        - slug (SlugField): Идентификатор страницы для URL.
        - description (TextField): Описание сообщества.
    """

    title = models.CharField(
        verbose_name='Название сообщества',
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='slug',
        unique=True,
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title[:TEXT_LEN]


class Post(models.Model):
    """Запись.

    Атрибуты:
        - author (ForeignKey): Ссылка на модель User, автора записи.
        - text (TextField): Текст записи.
        - pub_date (DateTimeField): Дата и время публикации записи.
        - image (ImageField): Изображение, (может быть пустым).
        - group (ForeignKey): Ссылка на модель Group. Сообщество, к которому
        относится запись.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    text = models.TextField(
        verbose_name='Текст записи',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        null=True,
        blank=True,
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Сообщество',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.text[:TEXT_LEN]


class Comment(models.Model):
    """Комментарий.

    Атрибуты:
        - author (ForeignKey): Ссылка на модель User, автора записи.
        - text (TextField): Текст комментария.
        - created (DateTimeField): Дата и время публикации комментария.
        - post (ForeignKey): Ссылка на модель Post, к которой относится
        комментарий.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Комментарий',
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:TEXT_LEN]


class Follow(models.Model):
    """Подписка.

    Атрибуты:
        - user (ForeignKey): Ссылка на модель User, представляющая подписчика.
        - following (ForeignKey): Ссылка на модель User, представляющая
        автора, на которого оформлена подписка.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following',
            )
        ]

    def __str__(self):
        return f'{self.user} подписчик автора - {self.following}'
