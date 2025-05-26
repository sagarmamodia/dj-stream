import aio_pika 
import asyncio
import redis 

r = redis.Redis(host='localhost', port=6379)
NOTIFICATIONS_CHANNEL = "notifications"
NOTIFICATIONS_QUEUE = "notifications"

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        raw = message.body
        text = raw.decode()
        r.publish(NOTIFICATIONS_CHANNEL, text)         
        print(f"{text} is put in the redis pub/sub.")

async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)

    await queue.consume(on_message)
    print("Waiting for messages... To exit press Ctrl + C")

    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
    r.close()
