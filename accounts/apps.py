from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Connect the signal that auto-creates a Profile for each new User
        from . import signals  # noqa: F401
