from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated


def custom_exception_handler(exc, context):
    # Вызываем стандартный обработчик исключений DRF
    response = exception_handler(exc, context)

    # Если ошибка связана с отсутствием аутентификации
    if isinstance(exc, NotAuthenticated):
        response.data = {
            "detail": "Учетные данные не были предоставлены."
        }

    # if isinstance(exc, NotFound):
    #     response.data = {
    #         "detail": "Страница не найдена."
    #     }
    return response
