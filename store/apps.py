from django.apps import AppConfig
 
 
class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'  # ← عدلي هذا لاسم الـ app تاعك
 
    def ready(self):
        import store.signals  # ← عدلي هذا لاسم الـ app تاعك
 