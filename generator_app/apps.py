# generator_app/apps.py
from django.apps import AppConfig

class GeneratorAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "generator_app"

    def ready(self):
        # при старте проекта пробегаем папку generators и регистрируем всё
        from .registry import controller
        controller.autodiscover_generators()
