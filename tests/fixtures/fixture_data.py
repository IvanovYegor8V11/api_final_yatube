import tempfile

import pytest


@pytest.fixture
def post(user):
    from posts.models import Post
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Post.objects.create(text='Тестовый пост 1', author=user, image=image)


@pytest.fixture
def post_2(user, group_1):
    from posts.models import Post
    return Post.objects.create(text='Тестовый пост 2', author=user, group=group_1)


@pytest.fixture
def comment_1_post(post, user):
    from posts.models import Comment
    return Comment.objects.create(author=user, post=post, text='Коммент 1')


@pytest.fixture
def comment_2_post(post, another_user):
    from posts.models import Comment
    return Comment.objects.create(author=another_user, post=post, text='Коммент 2')


@pytest.fixture
def another_post(another_user):
    from posts.models import Post
    return Post.objects.create(text='Тестовый пост 2', author=another_user)


@pytest.fixture
def comment_1_another_post(another_post, user):
    from posts.models import Comment
    return Comment.objects.create(author=user, post=another_post, text='Коммент 12')


@pytest.fixture
def group_1():
    from posts.models import Group
    return Group.objects.create(title='Группа 1', slug='group_1')


@pytest.fixture
def group_2():
    from posts.models import Group
    return Group.objects.create(title='Группа 2', slug='group_2')
