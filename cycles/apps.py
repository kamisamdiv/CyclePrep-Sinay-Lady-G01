from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CyclesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cycles'

    def ready(self):
        from .signals import seed_symptoms

        post_migrate.connect(seed_symptoms, sender=self)
