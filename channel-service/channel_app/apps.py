from django.apps import AppConfig
from . import rabbitmq


class ChannelAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'channel_app'

    def ready(self):
        # establishing the connection as soon as django loads up
        rabbitmq.get_connection()
        rabbitmq.get_channel()

