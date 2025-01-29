from http import HTTPStatus

from django.db.utils import IntegrityError
import pytest

from posts.models import Follow


@pytest.mark.django_db(transaction=True)
class TestFollowAPI:

    url = '/api/v1/follow/'

    def test_follow_not_found(self, user_client, follow_1, follow_2):
        response = user_client.get(self.url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url}` не найден, проверьте настройки в '
            '*urls.py*.'
        )

    def test_follow_not_auth(self, client, follow_1, follow_2):
        assert_msg = (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.url}` возвращает ответ со статусом 401.'
        )
        try:
            response = client.get(self.url)
        except TypeError as error:
            raise AssertionError(
                assert_msg + (
                    f' В процессе выполнения запроса произошла ошибка: {error}'
                )
            )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, assert_msg

        data = {}
        response = client.post(self.url, data=data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.url}` возвращает ответ со статусом 401.'
        )

    def test_follow_get(self, user_client, user, follow_1, follow_2, follow_3):
        response = user_client.get(self.url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.url}` возвращает ответ со статусом 200.'
        )

        test_data = response.json()
        assert isinstance(test_data, list), (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.url}` возвращает данные в виде списка.'
        )

        num_of_follows = (
            Follow.objects.filter(following__username=user.username).count()
        )
        assert len(test_data) == num_of_follows, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.url}` возвращает только данные о подписках '
            'пользователя.'
        )

        follow = Follow.objects.filter(user=user)[0]
        test_follow = test_data[0]
        expected_fields = ('user', 'following')
        for field in expected_fields:
            assert field in test_follow, (
                'Проверьте, что при GET-запросе авторизованного пользователя '
                f'к `{self.url}` в ответе содержится поле `{field}` для '
                'каждого объекта подписки.'
            )

        assert test_follow['user'] == follow.user.username, (
            'Проверьте, что при GET-запросе авторизованного '
            f'пользователя к `{self.url}` в поле `user` каждого из объектов '
            'подписки содержится корректный `username` пользователя.'
        )
        assert test_follow['following'] == follow.following.username, (
            'Проверьте, что в ответе на GET-запрос авторизованного '
            f'пользователя к `{self.url}` в поле `following` каждого из '
            'объектов подписки содержится корректный `username` '
            'автора, но которого подписан пользователь.'
        )

    def test_follow_create(self, user_client, follow_2, follow_3, user,
                           user_2, another_user):
        follow_count = Follow.objects.count()

        data = {}
        response = user_client.post(self.url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос с некорректными данными, '
            f'отправленный к `{self.url}`, возвращает ответ со статусом 400.'
        )

        assert_msg = (
            'Проверьте, что POST-запрос с корректными данными, отправленный '
            f'к `{self.url}`, возвращает ответ со статусом 201.'
        )
        data = {'following': another_user.username}
        try:
            response = user_client.post(self.url, data=data)
        except IntegrityError as error:
            raise AssertionError(
                assert_msg + (
                    f' В процессе выполнения запроса произошла ошибка: {error}'
                )
            )
        assert response.status_code == HTTPStatus.CREATED, assert_msg
        test_data = response.json()

        msg_error = (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.url}` возвращает словарь с данными новой подписки. '
            '{additional_msg}'
        )
        assert type(test_data) == dict, msg_error.format(additional_msg='')
        assert test_data.get('user') == user.username, (
            msg_error.format(
                additional_msg=('Сейчас ключ `user` отстутствует или '
                                'содержит некорректное значение.')
            )
        )
        assert test_data.get('following') == data['following'], (
            msg_error.format(
                additional_msg=('Сейчас ключ `following` отстутствует или '
                                'содержит некорректное значение.')
            )
        )
        assert follow_count + 1 == Follow.objects.count(), (
            'Проверьте, что POST-запрос с корректными данными, отправленный '
            f'авторизованным пользователем к `{self.url}`, создаёт новую '
            'подписку.'
        )

        assert_msg = (
            'Если в POST-запросе авторизованного '
            f'пользователя к `{self.url}` указан `username` автора, '
            'на которого пользователь уже подписан - должен вернуться ответ '
            'со статусом 400.'
        )
        try:
            response = user_client.post(self.url, data=data)
        except IntegrityError as error:
            raise AssertionError(
                assert_msg + (
                    f' В процессе выполнения запроса произошла ошибка: {error}'
                )
            )
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg

        data = {'following': user.username}
        response = user_client.post(self.url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что невозможно оформить подписку на самого себя через '
            f'POST-запрос к `{self.url}`. Такой запрос должен вернуть ответ '
            'со статусом 400.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_follow_search_filter(self, user_client, follow_1, follow_2,
                                  follow_3, follow_4, follow_5,
                                  user, user_2, another_user):

        user_follows = Follow.objects.filter(user=user)

        response = user_client.get(self.url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url}` не найден, проверьте настройки в '
            '*urls.py*.'
        )

        expected_len = user_follows.filter(following=user_2).count()
        response = user_client.get(f'{self.url}?search={user_2.username}')
        assert len(response.json()) == expected_len, (
            'Проверьте, что для авторизованного пользователя ответ на '
            f'GET-запрос с параметром `search` к `{self.url}` содержит только '
            'те подписки, которые удовлетворяют параметрам поиска.'
        )

        response = user_client.get(
            f'{self.url}?search={another_user.username}'
        )
        expected_len = user_follows.filter(following=another_user).count()
        assert len(response.json()) == expected_len, (
            'Проверьте, что для авторизованного пользователя ответ на '
            f'GET-запрос с параметром `search` к `{self.url}` содержит только '
            'те подписки, которые удовлетворяют параметрам поиска.'
        )
