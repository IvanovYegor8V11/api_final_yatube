# Проект API для Yatube
Проект в виде социальной сети с публикациями, комментариями, группами и подписками.

# Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/CatGamer7/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv .venv
```

```
source .venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

# Примеры некоторых запросов:
P.S. примеры всех запросов можно посмотреть в документации по адресу /redoc/

- Публикация поста
```
POST /api/v1/posts/
{
    "text": "string"
}
```

- Получение постов постранично
```
GET /api/v1/posts/?limit=10&offset=10
```

- Получение всех комменатриев

```
GET /api/v1/posts/{post_id}/comments/
```

- Удаление комментария

```
DEL /api/v1/posts/{post_id}/comments/{comment_id}/
```
