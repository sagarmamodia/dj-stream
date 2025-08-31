import time
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError
import os

ES_URL = f"http://{os.getenv('ES_HOST', 'localhost')}:{os.getenv('ES_PORT', 9200)}"
INDEX_NAME = "videos"


def get_es_client(retries=5, delay=5):
    """Try to connect to Elasticsearch with retries."""
    for attempt in range(1, retries + 1):
        try:
            es = Elasticsearch(ES_URL)
            if es.ping():
                print(f"✅ Connected to Elasticsearch at {ES_URL}")
                return es
            else:
                raise ESConnectionError("Elasticsearch ping failed")
        except ESConnectionError as e:
            print(f"⚠️ Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Could not connect to Elasticsearch after several attempts.")
                raise
    return None


# Create a global Elasticsearch client instance
es = get_es_client()

# Ensure index exists
if not es.indices.exists(index=INDEX_NAME):
    print(f"Creating index '{INDEX_NAME}'...")
    es.indices.create(
        index=INDEX_NAME,
        body={
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "channel_name": {"type": "keyword"},
                }
            }
        },
    )
    print(f"✅ Index '{INDEX_NAME}' created.")
else:
    print(f"ℹ️ Index '{INDEX_NAME}' already exists.")
