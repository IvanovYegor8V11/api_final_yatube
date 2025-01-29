# API для Yatube

### Как запустить проект:

Клонировать репозиторий и перейти в него в терминале:

```
git clone https://github.com/TheCatRiX/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас Windows

    ```
    source venv/Scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Перейти в директорию с manage.py и выполнить миграции:

```
cd yatube_api
```

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Документация:

После запуска проекта по адресу `http://localhost:8000/redoc/` будет доступна документация для API Yatube в формате Redoc.
