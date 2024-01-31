from django.apps import AppConfig

class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        try:
            import backend.signals  # Assuming you have signals defined
        except ImportError:
            pass
