from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception:  # never block app start
            import logging
            logging.getLogger(__name__).exception("Failed to start scheduler")
