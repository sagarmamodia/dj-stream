from fastapi import FastAPI, Depends
import pika
from utils import JsonResponse
from models import Likes, Dislikes, SubscriptionEntry, Comments, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete
import json
import uuid
import os

NOTIFICATIONS_QUEUE = 'notifications'
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', 5672)

def add_like(session: Session, user_id: str, video_id: str):
    user_uuid = uuid.UUID(user_id)
    video_uuid = uuid.UUID(video_id) 
    
    stmt = select(Likes).where(Likes.user_id==user_uuid, Likes.video_id==video_uuid)
    like_entry = session.execute(stmt).scalar_one_or_none()
    
    if like_entry is not None:
        return

    like_entry = Likes(user_id=user_uuid, video_id=video_uuid) 
    session.add(like_entry)
    session.commit()
    session.refresh(like_entry)

def remove_like(session:Session, user_id:str, video_id:str):
    user_uuid = uuid.UUID(user_id)
    video_uuid = uuid.UUID(video_id)
    stmt = select(Likes).where(Likes.user_id==user_uuid, Likes.video_id==video_uuid)

    like_entry = session.execute(stmt).scalar_one_or_none()
    
    if like_entry is not None:
        session.delete(like_entry) 
        session.commit()

def add_dislike(session: Session, user_id: str, video_id: str):
    user_uuid = uuid.UUID(user_id)
    video_uuid = uuid.UUID(video_id) 
    
    stmt = select(Dislikes).where(Dislikes.user_id==user_uuid, Dislikes.video_id==video_uuid)
    dislike_entry = session.execute(stmt).scalar_one_or_none()
    
    if dislike_entry is not None:
        return

    dislike_entry = Dislikes(user_id=user_id, video_id=video_id) 
    session.add(dislike_entry)
    session.commit()
    session.refresh(dislike_entry)

def remove_dislike(session: Session, user_id: str, video_id: str):
    user_uuid = uuid.UUID(user_id)
    video_uuid = uuid.UUID(video_id) 
    
    stmt = select(Dislikes).where(Dislikes.user_id==user_uuid, Dislikes.video_id==video_uuid)
    dislike_entry = session.execute(stmt).scalar_one_or_none()
    
    if dislike_entry is not None:
        session.delete(dislike_entry)
        session.commit()

def add_comment(session: Session, user_id:str, video_id:str, content:str):
    user_uuid = uuid.UUID(user_id)
    video_uuid = uuid.UUID(video_id) 
    
    comment_entry = Comments(user_id=user_uuid, video_id=video_uuid, content=content)
    session.add(comment_entry)
    session.commit()
    session.refresh(comment_entry)

def add_subscription(session: Session, user_id:str, channel_id:str):
    user_uuid = uuid.UUID(user_id)
    channel_uuid = uuid.UUID(channel_id) 
    
    #check if it already exists 
    stmt = select(SubscriptionEntry).where(SubscriptionEntry.user_id==user_uuid, SubscriptionEntry.channel_id==channel_uuid)
    entry = session.execute(stmt).scalar_one_or_none()

    if(entry is not None):
        return 
    
    entry = SubscriptionEntry(user_id=user_uuid, channel_id=channel_uuid)
    session.add(entry)
    session.commit()
    session.refresh(entry)

def remove_subscription(session:Session, user_id:str, channel_id:str):
    user_uuid = uuid.UUID(user_id)
    channel_uuid = uuid.UUID(channel_id) 
    
    #check if it already exists 
    stmt = select(SubscriptionEntry).where(SubscriptionEntry.user_id==user_uuid, SubscriptionEntry.channel_id==channel_uuid)
    entry = session.execute(stmt).scalar_one_or_none()

    if(entry is not None):
        session.delete(entry)
        session.commit()

def notify_subscribers(ch, session: Session, body: dict[str, str]):
    channel_id = body['channel_id']
    channel_name = body['channel_name']
    video_id = body['video_id']
    title = body['title']

    try:
        stmt = select(SubscriptionEntry).where(SubscriptionEntry.channel_id==uuid.UUID(channel_id))
        subscribers = session.execute(stmt).scalars().all()
    except:
        print("Failure to fetch subscribers from database")
        return

    for subscriber in subscribers:

        message = {
            "destination_user_id": str(subscriber.user_id),
            "payload": body
        }

        ch.basic_publish(
            exchange='',
            routing_key=NOTIFICATIONS_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2) 
        )

# ============ Consumer Code =================

QUEUE_NAME = "interaction-events"

def callback(ch, method, properties, body):
    body = json.loads(body)

    session = SessionLocal()
    if body['event'] == 'like':
        remove_dislike(session, body['user_id'], body['video_id'])
        add_like(session, body['user_id'], body['video_id'])

    elif body['event'] == 'remove_like':
        remove_like(session, body['user_id'], body['video_id'])

    elif body['event'] =='dislike':
        remove_like(session, body['user_id'], body['video_id'])
        add_dislike(session, body['user_id'], body['video_id'])

    elif body['event'] == 'remove_dislike':
        remove_dislike(session, body['user_id'], body['video_id'])

    elif body['event'] == 'comment':
        add_comment(session, body['user_id'], body['video_id'], body['content'])

    elif body['event'] == 'subscribe':
        add_subscription(session, body['user_id'], body['channel_id'])
 
    elif body['event'] == 'unsubscribe':
        remove_subscription(session, body['user_id'], body['channel_id'])

    elif body['event'] == 'video_uploaded':
        notify_subscribers(ch, session, body)

    print(f"{body['event']} event successfully consumed.")
    session.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection_parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)

    print(f"Waiting for messages...")
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    main()




