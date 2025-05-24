from fastapi import FastAPI, Depends
import pika
from utils import JsonResponse
import models
from sqlalchemy.orm import Session
import json
import uuid

QUEUE_NAME = "interaction-events"

def callback(ch, method, properties, body):
    body = json.loads(body)

    # update db
    session = models.SessionLocal()
    if body['event'] == 'like':
        user_id = uuid.UUID(body['user_id'])
        video_id = uuid.UUID(body['video_id'])
        like_entry = models.Likes(user_id=user_id, video_id=video_id) 
        session.add(like_entry)
        session.commit()
        session.refresh(like_entry)
        print(f"{user_id} liked {video_id}.")
    elif body['event'] =='dislike':
        user_id = uuid.UUID(body['user_id'])
        video_id = uuid.UUID(body['video_id'])
        dislike_entry = models.Dislikes(user_id=user_id, video_id=video_id) 
        session.add(dislike_entry)
        session.commit()
        session.refresh(dislike_entry)
        print(f"{user_id} disliked {video_id}.")
    elif body['comment'] == 'comment':
        user_id = uuid.UUID(body['user_id'])
        video_id = uuid.UUID(body['video_id'])
        content = body['content']
        comment_entry = models.Dislikes(user_id=user_id, video_id=video_id, content=content) 
        session.add(comment_entry)
        session.commit()
        session.refresh(dislike_entry)
        print(f"{user_id} commented {content} on {video_id}.")

    ch.basic_ack(delivery_tag=method.delivery_tag)
    session.close()

def main():
    connection_parameters = pika.ConnectionParameters(host='localhost')
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)

    print(f"Waiting for message...")
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    main()




