## Проект «API для Yatube»

Yatube - это социальная сеть, а проект "API для Yatube" предоставляет пользователям возможность взаимодействовать с функционалом платформы через программный интерфейс. Теперь можно публиковать посты, подписываться на авторов и управлять контентом с помощью API-запросов.

### Реализованы возможности

- Работа с постами: создание, обновление, удаление и получение списка публикаций.
- Работа с комментариями: добавление, редактирование, удаление и просмотр комментариев к постам.
- Просмотр сообществ: получение списка сообществ и их детальной информации.
- Подписки: просмотр подписок, а также возможность подписаться на интересующего автора.
- Авторизация: получение, обновление и проверка JWT-токенов для авторизации.

### Технологии

- [Python](https://www.python.org/) - язык программирования.
- [Django](https://www.djangoproject.com/) - свободный фреймворк для веб-приложений на языке Python.
- [Django REST Framework](https://www.django-rest-framework.org/) - мощный и гибкий набор инструментов для создания RESTful API.
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) - плагин аутентификации JSON Web Token для Django REST Framework.

### Запуск проекта:

Клонируйте репозиторий и перейдите в папку проекта:

`git clone https://github.com/apolwow/api_final_yatube.git`

`cd api_final_yatube`


Создайте и активируйте виртуальное окружение:

+ `python3 -m venv env`
+ `source env/bin/activate`
+ `python3 -m pip install --upgrade pip`

Установите зависимости из файла requirements.txt:
`pip install -r requirements.txt`

Выполните миграции базы данных:
`python3 manage.py migrate`


Запустите сервер разработки:
`python3 manage.py runserver`
#### После запуска документация API будет доступна по адресу:
`http://localhost:port/redoc/`

#### Примеры запросов:

POST-запрос с токеном, добавление новой публикации в коллекцию публикаций.

`POST http://localhost:port/api/v1/posts/`

```
{
  "text": "Привет, это мой первый пост!",
  "group": 1
}
```

Ответ:

```
{
    "id": 12,
    "author": "admin",
    "text": "Привет, это мой первый пост!",
    "pub_date": "2025-01-10T15:30:00Z",
    "image": null,
    "group": 1
}
```


GET-запрос, получение информации о сообществе по id=2.

`GET http://localhost:port/api/v1/groups/2/`

Ответ:

```
{
    "id": 1,
    "title": "Спорт",
    "slug": "sport",
    "description": "Группа для обсуждения спортивных событий."
}
```

POST-запрос, подписка авторизованного пользователя `user=admin` от имени которого сделан запрос на автора интересующей публикации `following=john_doe`.

`POST http://localhost:port/api/v1/follow/`

```
{
  "following": "john_doe"
}
```

Ответ:

```
{
    "id": 4,
    "user": "admin",
    "following": "john_doe"
}
```