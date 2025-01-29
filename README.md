# **API социальной сети "Yatube"**  

Проект представляет собой API-интерфейс для социальной сети "Yatube", позволяя взаимодействовать с ней через программные запросы.  


### **Шаг 1: Клонирование репозитория**  
```bash
git clone git@github.com:juliamekh/api_yatube.git
```

### **Шаг 2: Создание и активация виртуального окружения**  
```bash
python3 -m venv venv
source venv/bin/activate
```

### **Шаг 3: Установка зависимостей**  
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### **Шаг 4: Применение миграций**  
```bash
python3 manage.py migrate
```

### **Шаг 5: Создание суперпользователя**  
```bash
python3 manage.py createsuperuser
```

### **Шаг 6: Запуск сервера**  
```bash
python3 manage.py runserver
```

---

## **Примеры запросов API**  

### **Публикации (posts)**  

#### Получение списка публикаций (GET)  
`GET http://127.0.0.1:8000/api/v1/posts/`  


#### Создание публикации (POST)  
`POST http://127.0.0.1:8000/api/v1/posts/`  
```json
{
    "text": "Пример текста",
    "group": 1
}
```

#### Получение конкретной публикации (GET)  
`GET http://127.0.0.1:8000/api/v1/posts/{post_id}/`  

#### Обновление публикации (PUT)  
`PUT http://127.0.0.1:8000/api/v1/posts/{post_id}/`  
```json
{
    "text": "Обновленный текст",
    "image": "image_url",
    "group": 2
}
```

#### Удаление публикации (DELETE)  
`DELETE http://127.0.0.1:8000/api/v1/posts/{post_id}/`  
- Доступно только автору публикации  

---

### **Комментарии (comments)**  

#### Получение списка комментариев к публикации (GET)  
`GET http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/`

#### Добавление комментария (POST)  
`POST http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/`  
```json
{
    "text": "Комментарий к посту"
}
```
- Доступно только авторизованным пользователям  

#### Получение конкретного комментария (GET)  
`GET http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/{id}/`  

#### Обновление комментария (PUT)  
`PUT http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/{id}/`  

#### Удаление комментария (DELETE)  
`DELETE http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/{id}/`  
- Доступно только автору комментария  

---

### **Сообщества (groups)**  

#### Получение списка сообществ (GET)  
`GET http://127.0.0.1:8000/api/v1/groups/`  
- Доступно только авторизованным пользователям  

#### Получение информации о конкретном сообществе (GET)  
`GET http://127.0.0.1:8000/api/v1/groups/{id}/`


### **Подписки (follow)**  

#### Получение списка подписок пользователя (GET)  
`GET http://127.0.0.1:8000/api/v1/follow/`

#### Подписка на пользователя (POST)  
`POST http://127.0.0.1:8000/api/v1/follow/`  
```json
{
    "following": "username"
}
```
---

### **Аутентификация (JWT-токены)**  

#### Получение JWT-токена (POST)  
`POST http://127.0.0.1:8000/api/v1/jwt/create/`  
```json
{
    "username": "user",
    "password": "password"
}
```

#### Обновление JWT-токена (POST)  
`POST http://127.0.0.1:8000/api/v1/jwt/refresh/`  
```json
{
    "refresh": "токен"
}
```

#### Проверка JWT-токена (POST)  
`POST http://127.0.0.1:8000/api/v1/jwt/verify/`  
```json
{
    "token": "токен"
}
```