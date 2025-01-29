import pytest
from posts.models import Post


class TestPostAPI:

    @pytest.mark.django_db(transaction=True)
    def test_post_not_found(self, client, post):
        response = client.get('/api/v1/posts/')

        assert response.status_code != 404, (
                'Страница `/api/v1/posts/` не найдена, проверьте этот адрес в *urls.py*'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_not_auth(self, client, post):
        response = client.get('/api/v1/posts/')

        assert response.status_code == 401, (
            'Проверьте, что запросы на `/api/v1/posts/` '
            'доступны только аутентифицированным пользователям, '
            'а для неаутентифицированных возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_posts_auth_get(self, user_client, post, another_post):
        response = user_client.get('/api/v1/posts/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/posts/` с токеном авторизации возвращается статус 200'
        )

        test_data = response.json()
        assert type(test_data) == list, (
            'Проверьте, что при GET запросе на `/api/v1/posts/` возвращается список'
        )

        assert len(test_data) == Post.objects.count(), (
            'Проверьте, что при GET запросе на `/api/v1/posts/` возвращается весь список статей'
        )

        post = Post.objects.all()[0]
        test_post = test_data[0]
        assert 'id' in test_post, (
            'Проверьте, что добавили `id` в список полей `fields` сериализатора модели Post'
        )
        assert 'text' in test_post, (
            'Проверьте, что добавили `text` в список полей `fields` сериализатора модели Post'
        )
        assert 'author' in test_post, (
            'Проверьте, что добавили `author` в список полей `fields` сериализатора модели Post'
        )
        assert 'pub_date' in test_post, (
            'Проверьте, что добавили `pub_date` в список полей `fields` сериализатора модели Post'
        )
        assert test_post['author'] == post.author.username, (
            'Проверьте, что `author` сериализатора модели Post возвращает имя пользователя'
        )

        assert test_post['id'] == post.id, (
            'Проверьте, что при GET запросе на `/api/v1/posts/` возвращается весь список статей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_auth_create(self, user_client, user, another_user):
        post_count = Post.objects.count()

        data = {}
        response = user_client.post('/api/v1/posts/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/v1/posts/` с не правильными данными возвращается статус 400'
        )

        data = {'author': another_user.id, 'text': 'Статья номер 3'}
        response = user_client.post('/api/v1/posts/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на `/api/v1/posts/` с правильными данными возвращается статус 201'
        )

        test_data = response.json()

        msg_error = (
            'Проверьте, что при POST запросе на `/api/v1/posts/` возвращается словарь с данными новой статьи'
        )
        assert type(test_data) == dict, msg_error
        assert test_data.get('text') == data['text'], msg_error

        assert test_data.get('author') == user.username, (
            'Проверьте, что при POST запросе на `/api/v1/posts/` создается статья от авторизованного пользователя'
        )
        assert post_count + 1 == Post.objects.count(), (
            'Проверьте, что при POST запросе на `/api/v1/posts/` создается статья'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_unauth_create(self, client, user, another_user):
        posts_conut = Post.objects.count()

        data = {'author': another_user.id, 'text': 'Статья номер 3'}
        response = client.post('/api/v1/posts/', data=data)
        assert response.status_code == 401, (
            'Проверьте, что при POST запросе на `/api/v1/posts/` неавторизованному пользователю возвращается статус 401'
        )

        assert posts_conut == Post.objects.count(), (
            'Проверьте, что при POST запросе на `/api/v1/posts/` неавторизованный пользователь не может создать статью'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_get_current(self, user_client, post, user):
        response = user_client.get(f'/api/v1/posts/{post.id}/')

        assert response.status_code == 200, (
            'Страница `/api/v1/posts/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )

        test_data = response.json()
        assert test_data.get('text') == post.text, (
            'Проверьте, что при GET запросе `/api/v1/posts/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `text`'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что при GET запросе `/api/v1/posts/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `author`, должно возвращать имя пользователя '
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_patch_current(self, user_client, post, another_post):
        response = user_client.patch(f'/api/v1/posts/{post.id}/',
                                     data={'text': 'Поменяли текст статьи'})

        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` '
            'для авторизованного пользователя возвращаете статус 200'
        )

        test_post = Post.objects.filter(id=post.id).first()

        assert test_post, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` вы не удалили статью'
        )

        assert test_post.text == 'Поменяли текст статьи', (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` вы изменяете статью'
        )

        response = user_client.patch(f'/api/v1/posts/{another_post.id}/',
                                     data={'text': 'Поменяли текст статьи'})

        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` для не своей статьи возвращаете статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_auth_delete_current(self, user_client, post, another_post):
        response = user_client.delete(f'/api/v1/posts/{post.id}/')

        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` возвращаете статус 204'
        )

        test_post = Post.objects.filter(id=post.id).first()

        assert not test_post, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` вы удалили статью'
        )

        response = user_client.delete(f'/api/v1/posts/{another_post.id}/')

        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` для не своей статьи возвращаете статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_unauth_delete_current(self, client, post, another_post):
        post_count = Post.objects.count()
        response = client.delete(f'/api/v1/posts/{post.id}/')

        assert response.status_code == 401, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` '
            'неавторизованному пользователю возвращаете статус 401'
        )

        assert post_count == Post.objects.count(), (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` '
            'неавторизованный пользователь не может удалить статью'
        )

