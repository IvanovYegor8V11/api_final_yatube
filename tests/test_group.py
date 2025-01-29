import pytest
from posts.models import Group


class TestGroupAPI:

    @pytest.mark.django_db(transaction=True)
    def test_group_not_found(self, client, post, group_1):
        response = client.get('/api/v1/groups/')

        assert response.status_code != 404, (
            'Страница `/api/v1/groups/` не найдена, проверьте этот адрес в *urls.py*'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_not_auth(self, client, post, group_1):
        response = client.get('/api/v1/groups/')
        assert response.status_code == 401, (
            'Проверьте, что `/api/v1/groups/` при запросе без токена возвращаете статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_auth_get(self, user_client, post, another_post, group_1, group_2):
        response = user_client.get('/api/v1/groups/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/groups/` с токеном авторизации возвращается статус 200'
        )

        test_data = response.json()

        assert type(test_data) == list, (
            'Проверьте, что при GET запросе на `/api/v1/groups/` возвращается список'
        )

        assert len(test_data) == Group.objects.count(), (
            'Проверьте, что при GET запросе на `/api/v1/groups/` возвращается весь список групп'
        )

        groups_cnt = Group.objects.count()
        test_group = test_data[0]

        assert 'title' in test_group, (
            'Проверьте, что добавили `title` в список полей `fields` сериализатора модели Group'
        )

        assert len(test_data) == groups_cnt, (
            'Проверьте, что при GET запросе на `/api/v1/groups/` возвращается весь список групп'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_create(self, user_client, group_1, group_2):
        data = {'title': 'Группа  номер 3'}
        response = user_client.post('/api/v1/groups/', data=data)
        assert response.status_code == 405, (
            'Убедитесь, что создание группы недоступно через API, '
            'и при попытке сделать это, возвращается статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_get_post(self, user_client, post, post_2, another_post, group_1, group_2):
        response = user_client.get('/api/v1/posts/')
        assert response.status_code == 200, (
            'Страница `/api/v1/posts/` не найдена, проверьте этот адрес в *urls.py*'
        )
        test_data = response.json()
        assert len(test_data) == 3, (
            'Проверьте, что при GET запросе на `/api/v1/posts/` возвращается список всех постов'
        )
