import pika
import json
import time
from es_client import es, INDEX_NAME
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
SEARCH_EVENTS_QUEUE = "search-events-queue"


def is_es_healthy(retries=5, delay=3):
    """Check if Elasticsearch is healthy, retry a few times."""
    for attempt in range(1, retries + 1):
        try:
            if es.ping():
                print("✅ Elasticsearch is healthy and reachable")
                return True
            else:
                print(f"⚠️ Attempt {attempt}: Elasticsearch is not responding")
        except Exception as e:
            print(f"❌ Attempt {attempt}: Failed to connect to Elasticsearch: {e}")

        time.sleep(delay)

    return False


def callback(ch, method, properties, body):
    data = json.loads(body)
    video_id = data["video_id"]

    if not is_es_healthy():
        print(f"❌ Skipping indexing for {video_id} (Elasticsearch not healthy)")
        return

    try:
        es.index(
            index=INDEX_NAME,
            id=video_id,
            document={
                "title": data.get("title"),
                "description": data.get("description"),
                "channel_name": data.get("channel_name"),
            },
        )
        print(f" [x] Indexed video {video_id} into Elasticsearch")
    except Exception as e:
        print(f"❌ Failed to index video {video_id}: {e}")


def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=SEARCH_EVENTS_QUEUE, durable=True)
    channel.basic_consume(
        queue=SEARCH_EVENTS_QUEUE, on_message_callback=callback, auto_ack=True
    )

    print(f" [*] Waiting for messages in {SEARCH_EVENTS_QUEUE}. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
