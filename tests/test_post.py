from http import HTTPStatus

from django.db.utils import IntegrityError
import pytest

from posts.models import Post


@pytest.mark.django_db(transaction=True)
class TestPostAPI:

    VALID_DATA = {'text': 'Поменяли текст статьи'}
    post_list_url = '/api/v1/posts/'
    post_detail_url = '/api/v1/posts/{post_id}/'

    def check_post_data(self,
                        response_data,
                        request_method_and_url,
                        db_post=None):
        expected_fields = ('id', 'text', 'author', 'pub_date')
        for field in expected_fields:
            assert field in response_data, (
                'Проверьте, что для авторизованного пользователя ответ на '
                f'{request_method_and_url} содержит поле `{field}` постов.'
            )
        if db_post:
            assert response_data['author'] == db_post.author.username, (
                'Проверьте, что для авторизованного пользователя ответ на '
                f'{request_method_and_url} содержит поле `author` с '
                'именем автора каждого из постов.'
            )
            assert response_data['id'] == db_post.id, (
                'Проверьте, что для авторизованного пользователя ответ на '
                f'{request_method_and_url} содержится корректный `id` поста.'
            )

    def test_post_not_found(self, client, post):
        response = client.get(self.post_list_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.post_list_url}` не найден, проверьте настройки '
            'в *urls.py*.'
        )

    def test_post_list_not_auth(self, client, post):
        response = client.get(self.post_list_url)

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.post_list_url}` возвращает ответ со статусом 200.'
        )

    def test_post_single_not_auth(self, client, post):
        response = client.get(self.post_detail_url.format(post_id=post.id))

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.post_detail_url}` возвращает ответ со статусом 200.'
        )

    def test_posts_auth_get(self, user_client, post, another_post):
        response = user_client.get(self.post_list_url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.post_list_url}` возвращает статус 200.'
        )

        test_data = response.json()
        assert isinstance(test_data, list), (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.post_list_url}` возвращает список.'
        )

        assert len(test_data) == Post.objects.count(), (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.post_list_url}` возвращает список всех постов.'
        )

        db_post = Post.objects.first()
        test_post = test_data[0]
        self.check_post_data(
            test_post,
            f'GET-запрос к `{self.post_list_url}`',
            db_post
        )

    @pytest.mark.usefixtures('post', 'post_2', 'another_post')
    def test_posts_get_paginated(self, user_client):
        limit = 2
        offset = 2
        url = f'{self.post_list_url}?limit={limit}&offset={offset}'
        response = user_client.get(url)
        assert response.status_code == 200, (
            'Убедитесь, что GET-запрос с параметрами `limit` и `offset`, '
            'отправленный авторизованным пользователем к '
            f'`{self.post_list_url}`, возвращает ответ со статусом 200.'
        )

        test_data = response.json()

        # response with pagination must be a dict type
        assert isinstance(test_data, dict), (
            'Убедитесь, что GET-запрос с параметрами `limit` и `offset`, '
            'отправленный авторизованным пользователем к '
            f'`{self.post_list_url}`, возвращает словарь.'
        )
        assert "results" in test_data, (
            'Убедитесь, что GET-запрос с параметрами `limit` и `offset`, '
            'отправленный авторизованным пользователем к эндпоинту '
            f'`{self.post_list_url}`, содержит поле `results` с данными '
            'постов. Проверьте настройку пагинации для этого эндпоинта.'
        )
        assert len(test_data['results']) == Post.objects.count() - offset, (
            'Убедитесь, что GET-запрос с параметрами `limit` и `offset`, '
            'отправленный авторизованным пользователем к эндпоинту '
            f'`{self.post_list_url}`, возвращает корректное количество статей.'
        )

        db_post = Post.objects.all()[offset:offset + limit][0]
        test_post = test_data.get('results')[0]
        self.check_post_data(
            response_data=test_post,
            request_method_and_url=(
                f'GET-запрос к `{self.post_list_url} с указанием параметров '
                'запроса `limit` и `offset``'
            ),
            db_post=db_post
        )

    def test_post_create_auth_with_invalid_data(self, user_client):
        posts_count = Post.objects.count()
        response = user_client.post(self.post_list_url, data={})
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что для авторизованного пользователя POST-запрос с '
            f'некорректными данными к `{self.post_list_url}` возвращает ответ '
            'со статусом 400.'
        )
        assert posts_count == Post.objects.count(), (
            f'Проверьте, что POST-запрос с некорректными данными, '
            f'отправленный к `{self.post_list_url}`, не создаёт новый пост.'
        )

    def test_post_create_auth_with_valid_data(self, user_client, user,
                                              group_1):
        post_count = Post.objects.count()

        assert_msg = (
            'Проверьте, что для авторизованного пользователя  POST-запрос с '
            f'корректными данными к `{self.post_list_url}` возвращает ответ '
            'со статусом 201.'
        )
        data = {'text': 'Статья номер 3', 'group': group_1.id}
        try:
            response = user_client.post(self.post_list_url, data=data)
        except IntegrityError as error:
            raise AssertionError(
                assert_msg + (
                    f' В процессе выполнения запроса произошла ошибка: {error}'
                )
            )
        assert response.status_code == HTTPStatus.CREATED, assert_msg
        post_count += 1

        test_data = response.json()
        assert isinstance(test_data, dict), (
            'Проверьте, что для авторизованного пользователя POST-запрос к '
            f'`{self.post_list_url}` возвращает ответ, содержащий данные '
            'нового поста в виде словаря.'
        )
        self.check_post_data(
            test_data, f'POST-запрос к `{self.post_list_url}`'
        )
        assert test_data.get('text') == data['text'], (
            'Проверьте, что для авторизованного пользователя POST-запрос к '
            f'`{self.post_list_url}` возвращает ответ, содержащий текст '
            'нового поста в неизменном виде.'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что для авторизованного пользователя при создании '
            f'поста через POST-запрос к `{self.post_list_url}` ответ содержит '
            'поле `author` с именем пользователя, отправившего запрос.'
        )
        assert test_data.get('group') == group_1.id, (
            'Проверьте, что для авторизованного пользователя при создании '
            f'поста через POST-запрос к `{self.post_list_url}` с указанием '
            'группы ответ содержит поле `group` с `id` указанной в запросе '
            'группы.'
        )

        data = {'text': 'Статья номер 3'}
        response = user_client.post(self.post_list_url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если в POST-запросе, отправленном авторизованным пользователем '
            f'на `{self.post_list_url}`, не переданы данные о группе - '
            'должен вернуться ответ со статусом 201.'
        )
        post_count += 1

        assert post_count == Post.objects.count(), (
            'Проверьте, что POST-запрос с корректными данными от '
            f'авторизованного пользователя к `{self.post_list_url}` создаёт '
            'новый пост.'
        )

    def test_post_unauth_create(self, client, user, another_user):
        posts_conut = Post.objects.count()

        data = {'author': another_user.id, 'text': 'Статья номер 3'}
        assert_msg = (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.post_list_url}` возвращает ответ со статусом 401.'
        )
        try:
            response = client.post(self.post_list_url, data=data)
        except ValueError as error:
            raise AssertionError(
                assert_msg + (
                    '\nВ процессе выполнения запроса произошла ошибка: '
                    f'{error}'
                )
            )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, assert_msg

        assert posts_conut == Post.objects.count(), (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.post_list_url}` не создаёт новый пост.'
        )

    def test_post_get_current(self, user_client, post):
        response = user_client.get(
            self.post_detail_url.format(post_id=post.id)
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.post_detail_url}` возвращает ответ со статусом 200.'
        )

        test_data = response.json()
        self.check_post_data(
            test_data,
            f'GET-запрос к `{self.post_detail_url}`',
            post
        )

    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_auth_with_valid_data(self, user_client, post,
                                              another_post, http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(
            self.post_detail_url.format(post_id=post.id),
            data=self.VALID_DATA
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте, что {http_method}-запрос авторизованного '
            f'пользователя, отправленный на `{self.post_detail_url}` к '
            'собственному посту, вернёт ответ со статусом 200.'
        )

        test_post = Post.objects.filter(id=post.id).first()
        assert test_post, (
            f'Проверьте, что {http_method}-запрос авторизованного '
            f'пользователя, отправленный на `{self.post_detail_url}` к '
            'собственному посту, не удаляет редактируемый пост.'
        )
        assert test_post.text == self.VALID_DATA['text'], (
            f'Проверьте, что {http_method}-запрос авторизованного '
            f'пользователя, отправленный на `{self.post_detail_url}` к '
            'собственному посту, вносит изменения в пост.'
        )

    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_not_auth_with_valid_data(self, client, post,
                                                  http_method):
        request_func = getattr(client, http_method)
        response = request_func(
            self.post_detail_url.format(post_id=post.id),
            data=self.VALID_DATA
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте, что {http_method}-запрос неавторизованного '
            f'пользователя к `{self.post_detail_url}` возвращает ответ со '
            'статусом 401.'
        )
        db_post = Post.objects.filter(id=post.id).first()
        assert db_post.text != self.VALID_DATA['text'], (
            f'Проверьте, что {http_method}-запрос неавторизованного '
            f'пользователя к `{self.post_detail_url}` не вносит изменения в '
            'пост.'
        )

    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_not_author_with_valid_data(self, user_client,
                                                    another_post, http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(
            self.post_detail_url.format(post_id=another_post.id),
            data=self.VALID_DATA
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            f'Проверьте, что {http_method}-запрос авторизованного '
            f'пользователя, отправленный на `{self.post_detail_url}` к чужому '
            'посту, возвращает ответ со статусом 403.'
        )

        db_post = Post.objects.filter(id=another_post.id).first()
        assert db_post.text != self.VALID_DATA['text'], (
            f'Проверьте, что {http_method}-запрос авторизованного '
            f'пользователя, отправленный на `{self.post_detail_url}` к чужому '
            'посту, возвращает ответ со статусом 403.'
        )

    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_patch_auth_with_invalid_data(self, user_client, post,
                                               http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(
            self.post_detail_url.format(post_id=post.id),
            data={'text': {}},
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте, что {http_method}-запрос с некорректными данными от '
            f'авторизованного пользователя к `{self.post_detail_url}` '
            'возвращает ответ с кодом 400.'
        )

    def test_post_delete_by_author(self, user_client, post):
        response = user_client.delete(
            self.post_detail_url.format(post_id=post.id)
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что для автора поста DELETE-запрос к '
            f'`{self.post_detail_url}` возвращает ответ со статусом 204.'
        )

        test_post = Post.objects.filter(id=post.id).first()
        assert not test_post, (
            'Проверьте, что DELETE-запрос автора поста к '
            ' `/api/v1/posts/{id}/` удаляет этот пост.'
        )

    def test_post_delete_not_author(self, user_client, another_post):
        response = user_client.delete(
            self.post_detail_url.format(post_id=another_post.id)
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос авторизованного пользователя, '
            f'отправленный на `{self.post_detail_url}` к чужому посту, вернёт '
            'ответ со статусом 403.'
        )

        test_post = Post.objects.filter(id=another_post.id).first()
        assert test_post, (
            'Проверьте, что авторизованный пользователь не может удалить '
            'чужой пост.'
        )

    def test_post_unauth_delete_current(self, client, post):
        response = client.delete(
            self.post_detail_url.format(post_id=post.id)
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя '
            f'к `{self.post_detail_url}` вернёт ответ со статусом 401.'
        )
        test_post = Post.objects.filter(id=post.id).first()
        assert test_post, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя '
            f'к `{self.post_detail_url}` не удаляет запрошенный пост.'
        )
