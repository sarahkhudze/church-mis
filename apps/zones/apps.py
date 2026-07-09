from django.apps import AppConfig

class ZonesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.zones'  # Make sure this is 'apps.zones' not just 'zones'
    verbose_name = 'Zone Management'