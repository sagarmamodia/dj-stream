import pika 
import atexit
from django.conf import settings

_connection = None
_channel = None

def get_connection():
    global _connection 
    if _connection is None or _connection.is_closed:
        params = pika.URLParameters(settings.RABBITMQ_URL)
        _connection = pika.BlockingConnection(params)

    return _connection

def get_channel():
    global _channel 
    if _channel is None or _channel.is_closed:
        _channel = get_connection().channel()

    return _channel
    

def close_connection():
    global _channel, _connection
    if _channel and not _channel.is_closed:
        _channel.close()

    if _connection and not _connection.is_closed:
        _connection.close()

# register this function to run as soon as our program is about to exit
atexit.register(close_connection)
