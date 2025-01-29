import pytest
from django.conf import settings


class TestAuthAPI:

    def test_settings(self):
        assert hasattr(settings, 'REST_FRAMEWORK'), (
            'Проверьте, что добавили настройку `REST_FRAMEWORK` в файл `settings.py`'
        )

        assert 'DEFAULT_AUTHENTICATION_CLASSES' in settings.REST_FRAMEWORK, (
            'Проверьте, что добавили `DEFAULT_AUTHENTICATION_CLASSES` в `REST_FRAMEWORK` файла `settings.py`'
        )
        assert (
                'rest_framework.authentication.TokenAuthentication' in
                settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']
        ), (
            "Проверьте, что в списке значения `DEFAULT_AUTHENTICATION_CLASSES` в `REST_FRAMEWORK` "
            "содержится 'rest_framework.authentication.TokenAuthentication'"
        )

    @pytest.mark.django_db(transaction=True)
    def test_auth(self, client, user):

        response = client.post(
            '/api/v1/api-token-auth/', data={'username': user.username, 'password': '1234567'}
        )

        assert response.status_code != 404, (
            'Страница `/api/v1/api-token-auth/` не найдена, проверьте этот адрес в *urls.py*'
        )

        assert response.status_code == 200, (
            'Страница `/api/v1/api-token-auth/` работает не правильно'
        )

        auth_data = response.json()
        assert 'token' in auth_data, (
            'Проверьте, что при POST запросе `/api/v1/api-token-auth/` возвращаете токен'
        )
