from django.apps import AppConfig


class AppticketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appticket'

    def ready(self):
        from django.contrib.auth.models import Group
        for group_name in ['agent', 'administrateur']:
            Group.objects.get_or_create(name=group_name)
