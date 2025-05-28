import pika 

connection_parameters = pika.ConnectionParameters(host='localhost')
connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue="notifications", durable=True)

channel.basic_publish(
    exchange='',
    routing_key='notifications',
    body='{"payload": {"message": "hello world!"}, "destination_user_id": "3df6cb86-619b-4622-b93a-924b34c638b4"}',
    properties=pika.BasicProperties(delivery_mode=2)
)
