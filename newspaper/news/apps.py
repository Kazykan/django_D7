from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """настройка для работы файла signal.py так же поправлен INSTALLED_APPS 'news.apps.NewsConfig' """
        import news.signals
