import aio_pika 
import asyncio
import redis 
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', 5672)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
NOTIFICATIONS_CHANNEL = "notifications"
NOTIFICATIONS_QUEUE = "notifications"

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        raw = message.body
        text = raw.decode()
        r.publish(NOTIFICATIONS_CHANNEL, text)         
        print(f"{text} is put in the redis pub/sub.")

async def main():
    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/")
    channel = await connection.channel()
    queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)

    await queue.consume(on_message)
    print("Waiting for messages... To exit press Ctrl + C")

    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
    r.close()
