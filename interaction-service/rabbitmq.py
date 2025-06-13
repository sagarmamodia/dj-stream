import pika
import json
import os

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

class RabbitMQ:
    def __init__(self):
        self.connection = None
        self.channel = None 

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        self.channel = self.connection.channel()
        print("Connected to RabbitMQ.")

    def publish(self, message: dict, queue_name: str):
        if self.channel is None:
            print("Not connected to rabbitmq")
            return 

        message = json.dumps(message)
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except:
            print("Failure to put message in the queue")

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close() 
