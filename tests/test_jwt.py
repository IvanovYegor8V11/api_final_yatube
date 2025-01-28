from http import HTTPStatus

import pytest


@pytest.mark.django_db(transaction=True)
class TestJWT:
    url_create = '/api/v1/jwt/create/'
    url_refresh = '/api/v1/jwt/refresh/'
    url_verify = '/api/v1/jwt/verify/'

    def check_request_with_invalid_data(self, client, url, invalid_data,
                                        expected_fields):
        response = client.post(url)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный к `{url}`, не содержит всех '
            'необходимых данных - должен вернуться ответ со статусом 400.'
        )

        response = client.post(url, data=invalid_data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Убедитесь, что POST-запрос с некорректными данными, '
            f'отправленный к `{url}`, возвращает ответ со статусом 401.'
        )
        for field in expected_fields:
            assert field in response.json(), (
                'Убедитесь, что в ответе на POST-запрос с некорректными '
                f'данными, отправленный к `{url}`, содержится поле `{field}` '
                'с соответствующим сообщением.'
            )

    def test_jwt_create__invalid_request_data(self, client, user):
        url = self.url_create
        response = client.post(url)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что POST-запрос без необходимых данных, отправленный '
            f'к `{url}`, возвращает ответ со статусом код 400.'
        )
        fields_invalid = ['username', 'password']
        for field in fields_invalid:
            assert field in response.json(), (
                'Убедитесь, что в ответе на POST-запрос без необходимых '
                'данных, отправленный к `{url}` содержится информация об '
                'обязательных для этого эндпоинта полях. Сейчас ответ не '
                f'содержит информацию о поле `{field}`.'
            )

        invalid_data = (
            {
                'username': 'invalid_username_not_exists',
                'password': 'invalid pwd'
            },
            {
                'username': user.username,
                'password': 'invalid pwd'
            }
        )
        field = 'detail'
        for data in invalid_data:
            response = client.post(url, data=data)
            assert response.status_code == HTTPStatus.UNAUTHORIZED, (
                'Убедитесь, что POST-запрос с некорректными данными, '
                f'отправленный к`{url}`, возвращает ответ со статусом 401.'
            )
            assert field in response.json(), (
                'Убедитесь, что в ответе на POST-запрос с некорректными '
                f'данными, отправленный к `{url}`, содержится поле `{field}` '
                'с сообщением об ошибке.'
            )

    def test_jwt_create__valid_request_data(self, client, user):
        url = self.url_create
        valid_data = {
            'username': user.username,
            'password': '1234567'
        }
        response = client.post(url, data=valid_data)
        assert response.status_code == HTTPStatus.OK, (
            'Убедитесь, что POST-запрос с корректными данными, отправленный '
            f'к `{url}`, возвращает ответ со статусом 200.'
        )
        fields_in_response = ['refresh', 'access']
        for field in fields_in_response:
            assert field in response.json(), (
                'Убедитесь, что в ответе на  POST-запрос с корректными '
                f'данными, отправленный к `{url}`, содержится поле `{field}` '
                'с соответствующим токеном.'
            )

    def test_jwt_refresh__invalid_request_data(self, client):
        invalid_data = {
            'refresh': 'invalid token'
        }
        fields_expected = ['detail', 'code']
        self.check_request_with_invalid_data(
            client, self.url_refresh, invalid_data, fields_expected
        )

    def test_jwt_refresh__valid_request_data(self, client, user):
        url = self.url_refresh
        valid_data = {
            'username': user.username,
            'password': '1234567'
        }
        response = client.post(self.url_create, data=valid_data)
        token_refresh = response.json().get('refresh')
        response = client.post(url, data={'refresh': token_refresh})
        assert response.status_code == HTTPStatus.OK, (
            'Убедитесь, что POST-запрос с корректными данными, отправленный '
            f'к `{url}`, возвращает ответ со статусом 200.'
        )
        field = 'access'
        assert field in response.json(), (
            'Убедитесь, что в ответе на POST-запрос с корректными данными, '
            f'отправленный к `{url}`, содержится поле `{field}`, '
            'содержащее новый токен.'
        )

    def test_jwt_verify__invalid_request_data(self, client):
        invalid_data = {
            'token': 'invalid token'
        }
        fields_expected = ['detail', 'code']
        self.check_request_with_invalid_data(
            client, self.url_verify, invalid_data, fields_expected
        )

    def test_jwt_verify__valid_request_data(self, client, user):
        url = self.url_verify
        valid_data = {
            'username': user.username,
            'password': '1234567'
        }
        response = client.post(self.url_create, data=valid_data)
        response_data = response.json()

        for token in (response_data.get('access'),
                      response_data.get('refresh')):
            response = client.post(url, data={'token': token})
            assert response.status_code == HTTPStatus.OK, (
                'Убедитесь, что POST-запрос с корректными данными, '
                f'отправленный к `{url}`, возвращает ответ со статусом 200. '
                'Корректными данными считаются `refresh`- и `access`-токены.'
            )
