from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        from .signals import user_registered, handle_user_registered
        user_registered.connect(handle_user_registered)