from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Конфигурация приложения accounts."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """Импортирует сигналы при готовности приложения."""
        import accounts.signals