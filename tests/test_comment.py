from http import HTTPStatus

from django.db.utils import IntegrityError
import pytest

from posts.models import Comment


@pytest.mark.django_db(transaction=True)
class TestCommentAPI:

    TEXT_FOR_COMMENT = 'Новый комментарий'
    comments_url = '/api/v1/posts/{post_id}/comments/'
    comment_detail_url = (
        '/api/v1/posts/{post_id}/comments/{comment_id}/'
    )

    def check_comment_data(self,
                           response_data,
                           request_method_and_url,
                           db_comment=None):
        expected_fields = ('id', 'text', 'author', 'post', 'created')
        for field in expected_fields:
            assert field in response_data, (
                'Проверьте, что для авторизованного пользователя при '
                f'{request_method_and_url} ответ содержит поле '
                f'комментария `{field}`.'
            )
        if db_comment:
            assert response_data['author'] == db_comment.author.username, (
                'Проверьте, что для авторизованного пользователя при '
                f'{request_method_and_url} ответ содержит поле '
                'комментария `author`, и в этом поле указан `username` автора '
                'комментария.'
            )
            assert response_data['id'] == db_comment.id, (
                'Проверьте, что для авторизованного пользователя при '
                f'{request_method_and_url} ответ содержит корректный '
                '`id` комментария.'
            )

    def test_comments_not_authenticated(self, client, post):
        response = client.get(
            self.comments_url.format(post_id=post.id)
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.comments_url}` возвращает ответ со статусом 200.'
        )

    def test_comment_single_not_authenticated(self, client, post,
                                              comment_1_post):
        response = client.get(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_1_post.id
            )
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.comment_detail_url}` возвращает ответ со статусом 200.'
        )

    def test_comments_not_found(self, user_client, post):
        response = user_client.get(
            self.comments_url.format(post_id=post.id)
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.comments_url}` не найден, проверьте настройки в '
            '*urls.py*.'
        )

    def test_comments_id_available(self, user_client, post, comment_1_post):
        response = user_client.get(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_1_post.id
            )
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.comment_detail_url}` не найден, проверьте '
            'настройки в *urls.py*.'
        )

    def test_comments_get(self, user_client, post, comment_1_post,
                          comment_2_post, comment_1_another_post):
        response = user_client.get(
            self.comments_url.format(post_id=post.id)
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            f'`{self.comments_url}` возвращается ответ со статусом 200.'
        )
        test_data = response.json()
        assert isinstance(test_data, list), (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            f'`{self.comments_url}` данные возвращаются в виде списка.'
        )
        assert len(test_data) == Comment.objects.filter(post=post).count(), (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            f'`{self.comments_url}` возвращаются данные о комментариях '
            'только к конкретному посту.'
        )

        comment = Comment.objects.filter(post=post).first()
        test_comment = test_data[0]
        self.check_comment_data(
            test_comment,
            f'GET-запросе к `{self.comments_url}`',
            db_comment=comment
        )

    def test_comment_create_by_unauth(self, client, post, comment_1_post):
        comment_cnt = Comment.objects.count()

        assert_msg = (
            'Проверьте, что для неавторизованного пользователя POST-запрос '
            f'к `{self.comments_url}` возвращает ответ со статусом 401.'
        )
        data = {'text': self.TEXT_FOR_COMMENT}
        try:
            response = client.post(
                self.comments_url.format(post_id=post.id),
                data=data
            )
        except ValueError as error:
            raise AssertionError(
                assert_msg + (
                    '\nВ процессе выполнения запроса произошла ошибка: '
                    f'{error}'
                )
            )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, assert_msg
        assert comment_cnt == Comment.objects.count(), (
            'Проверьте, что POST-запрос неавторизованного пользователя, '
            f'отправленный к `{self.comment_detail_url}`, не создаёт '
            'комментарий.'
        )

    def test_comments_post_auth_with_valid_data(self, user_client, post,
                                                user, another_user):
        comments_count = Comment.objects.count()

        assert_msg = (
            'Проверьте, что POST-запрос с корректными данными от '
            f'авторизованного пользователя к `{self.comments_url}` возвращает '
            'ответ со статусом 201.'
        )
        data = {'text': self.TEXT_FOR_COMMENT}
        try:
            response = user_client.post(
                self.comments_url.format(post_id=post.id),
                data=data
            )
        except IntegrityError as error:
            raise AssertionError(
                assert_msg + (
                    f' В процессе выполнения запроса произошла ошибка: {error}'
                )
            )
        assert response.status_code == HTTPStatus.CREATED, assert_msg

        test_data = response.json()
        assert isinstance(test_data, dict), (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращает ответ, '
            'содержащий данные нового комментария в виде словаря.'
        )
        assert test_data.get('text') == data['text'], (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.comments_url}` возвращает ответ, содержащий текст нового '
            'комментария в неизменном виде.'
        )
        self.check_comment_data(
            test_data,
            f'POST-запросе к `{self.comments_url}`'
        )

        assert test_data.get('author') == user.username, (
            'Проверьте, что при создании комментария через POST-запрос к '
            f'`{self.comments_url}` авторизованный пользователь '
            'получит ответ, в котором будет поле `author` с его `username`.'
        )
        assert comments_count + 1 == Comment.objects.count(), (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.comments_url}` создаёт новый комментарий.'
        )

    def test_comments_auth_post_with_invalid_data(self, user_client, post):
        comments_count = Comment.objects.count()

        response = user_client.post(
            self.comments_url.format(post_id=post.id),
            data={}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос с некорректными данными от '
            f'авторизованного пользователя к `{self.comments_url}` возвращает '
            'ответ со статусом 400.'
        )
        assert comments_count == Comment.objects.count(), (
            'Проверьте, что при POST-запросе с некорректными данными к '
            f'`{self.comments_url}` новый комментарий не создаётся.'
        )

    def test_comment_author_and_post_are_read_only(self, user_client, post):
        response = user_client.post(
            self.comments_url.format(post_id=post.id),
            data={}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос с некорректными данными от '
            f'авторизованного пользователя к `{self.comments_url}` возвращает '
            'ответ со статусом 400.'
        )
        data = set(response.json())
        assert not {'author', 'post'}.intersection(data), (
            f'Проверьте, что для эндпоинта `{self.comments_url}` для полей '
            '`author` и `post` установлен свойство "Только для чтения".'
        )

    def test_comment_id_auth_get(self, user_client, post,
                                 comment_1_post, user):
        response = user_client.get(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_1_post.id
            )
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.comment_detail_url}` возвращает ответ со статусом 200.'
        )

        test_data = response.json()
        assert test_data.get('text') == comment_1_post.text, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            f'`{self.comment_detail_url}` возвращает ответ, содержащий текст '
            'комментария.'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            f'`{self.comment_detail_url}` возвращает ответ, содержащий '
            '`username` автора комментария.'
        )
        assert test_data.get('post') == post.id, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            f'{self.comment_detail_url}` возвращает ответ, содержащий `id` '
            'поста.'
        )

    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_comment_change_by_auth_with_valid_data(self,
                                                    user_client,
                                                    post,
                                                    comment_1_post,
                                                    comment_2_post,
                                                    http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_1_post.id
            ),
            data={'text': self.TEXT_FOR_COMMENT}
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте, что {http_method}-запрос, отправленный '
            'авторизованным пользователем на эндпоинт '
            f'`{self.comment_detail_url}` к собственному комментарию, '
            'возвращает ответ со статусом 200.'
        )

        db_comment = Comment.objects.filter(id=comment_1_post.id).first()
        assert db_comment, (
            f'Проверьте, что {http_method}-запрос, отправленный '
            'авторизованным пользователем на эндпоинт '
            f'`{self.comment_detail_url}` к собственному комментарию, вернёт '
            'ответ со статусом 200.'
        )
        assert db_comment.text == self.TEXT_FOR_COMMENT, (
            f'Проверьте, что {http_method}-запрос, отправленный '
            'авторизованным пользователем на эндпоинт '
            f'`{self.comment_detail_url}` к собственному комментарию, вносит '
            'изменения в комментарий.'
        )
        response_data = response.json()
        self.check_comment_data(
            response_data,
            request_method_and_url=(
                f'{http_method}-запросе к {self.comment_detail_url}'
            ),
            db_comment=db_comment
        )

    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_comment_change_not_auth_with_valid_data(self,
                                                     client,
                                                     post,
                                                     comment_1_post,
                                                     http_method):
        request_func = getattr(client, http_method)
        response = request_func(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_1_post.id
            ),
            data={'text': self.TEXT_FOR_COMMENT}
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте, что для неавторизованного пользователя {http_method}'
            f'-запрос к `{self.comment_detail_url}` возвращает ответ со '
            'статусом 401.'
        )
        db_comment = Comment.objects.filter(id=comment_1_post.id).first()
        assert db_comment.text != self.TEXT_FOR_COMMENT, (
            f'Проверьте, что для неавторизованного пользователя {http_method}'
            f'-запрос к `{self.comment_detail_url}` не вносит изменения в '
            'комментарий.'
        )

    def test_comment_delete_by_author(self, user_client,
                                      post, comment_1_post):
        response = user_client.delete(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_1_post.id
            )
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос, отправленный авторизованным '
            'пользователем к собственному комментарию на эндпоинт '
            f'`{self.comment_detail_url}`, возвращает ответ со статусом 204.'
        )

        test_comment = Comment.objects.filter(id=post.id).first()
        assert not test_comment, (
            'Проверьте, что DELETE-запрос автора комментария к '
            f'`{self.comment_detail_url}` удаляет комментарий.'
        )

    def test_comment_delete_by_not_author(self, user_client,
                                          post, comment_2_post):
        response = user_client.delete(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_2_post.id
            )
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос, отправленный авторизованным '
            'пользователем к чужому комментарию на эндпоинт '
            f'`{self.comment_detail_url}`, возвращает ответ со статусом 403.'
        )
        db_comment = Comment.objects.filter(id=comment_2_post.id).first()
        assert db_comment, (
            'Проверьте, что DELETE-запрос авторизованного пользователя  к '
            f'чужому комментарию на эндпоинт `{self.comment_detail_url}` не '
            'удаляет этот комментарий.'
        )

    def test_comment_delete_by_unauth(self, client, post, comment_1_post):
        response = client.delete(
            self.comment_detail_url.format(
                post_id=post.id, comment_id=comment_1_post.id
            )
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что для неавторизованного пользователя DELETE-запрос '
            f'к `{self.comment_detail_url}` возвращает ответ со статусом 401.'
        )
        db_comment = Comment.objects.filter(id=comment_1_post.id).first()
        assert db_comment, (
            'Проверьте, что для неавторизованного пользователя DELETE-запрос '
            f'к `{self.comment_detail_url}` не удаляет комментарий.'
        )
