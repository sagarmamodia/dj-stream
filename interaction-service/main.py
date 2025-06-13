from fastapi import FastAPI, Depends, Request
import pika
from utils import JsonResponse, is_valid_uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import models
import schemas
import uuid
from rabbitmq import RabbitMQ
import uvicorn
import os

app = FastAPI()
mq = RabbitMQ()

# session generator
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# rabbitmq 
EVENTS_QUEUE = "interaction-events"
NOTIFICATIONS_QUEUE = "notifications"

@app.on_event("startup")
def startup():
    mq.connect()

@app.on_event("shutdown")
def shutdown():
    mq.close()

@app.get('/home/')
def home():
    return JsonResponse(resp="Welcome to interaction_service")

@app.get('/interaction/likes/{video_id}/', response_model=schemas.LikesResponse)
def get_likes(video_id: str, session: Session=Depends(get_db)):
    try:
        stmt = select(func.count()).where(Likes.video_id==video_id)
        result = session.execute(stmt).scalar()
    except:
        return JsonResponse(error="Failure to fetch likes data from database", status=500)

    response = schemas.LikesResponse(video_id=video_id, likes=result)

    return response

@app.post('/interaction/auth_required/add_like/{video_id}/')
def like_video(request: Request, video_id: str):
    if(not is_valid_uuid(video_id)):
        return JsonResponse(error="{video_id} is not a valid ID", status=400)

    try:
        user_id = request.headers.get('X-User-ID')
    except:
        return JsonResponse(error="Request not authorized", status=401)

    try:
        mq.publish({"event": "like", "video_id": video_id, "user_id": user_id}, EVENTS_QUEUE)
    except:
        return JsonResponse(error="Could not update database", status=500)
    
    return JsonResponse(status=200)

@app.post('/interaction/auth_required/remove_like/{video_id}/')
def remove_like_video(request: Request, video_id: str):
    if(not is_valid_uuid(video_id)):
        return JsonResponse(error="{video_id} is not a valid ID", status=400)

    try:
        user_id = request.headers.get('X-User-ID')
    except:
        return JsonResponse(error="Request not authorized", status=401)

    try:
        mq.publish({"event": "remove_like", "video_id": video_id, "user_id": user_id}, EVENTS_QUEUE)
    except:
        return JsonResponse(error="Could not update database", status=500)
    
    return JsonResponse(status=200)


@app.post('/interaction/auth_required/add_dislike/{video_id}/')
def dislike_video(request: Request, video_id: str):
    if(not is_valid_uuid(video_id)):
        return JsonResponse(error="{video_id} is not a valid ID", status=400)

    try:
        user_id = request.headers.get('X-User-ID')
    except:
        return JsonResponse(error="Request not authorized", status=401)

    try:
        mq.publish({"event": "dislike", "video_id": video_id, "user_id": user_id}, EVENTS_QUEUE)
    except:
        return JsonResponse(error="Could not update database", status=500)
    
    return JsonResponse(status=200)

@app.post('/interaction/auth_required/remove_dislike/{video_id}/')
def remove_dislike_video(request: Request, video_id: str):
    if(not is_valid_uuid(video_id)):
        return JsonResponse(error="{video_id} is not a valid ID", status=400)

    try:
        user_id = request.headers.get('X-User-ID')
    except:
        return JsonResponse(error="Request not authorized", status=401)

    try:
        mq.publish({"event": "remove_dislike", "video_id": video_id, "user_id": user_id}, EVENTS_QUEUE)
    except:
        return JsonResponse(error="Could not update database", status=500)
    
    return JsonResponse(status=200)


@app.post('/interaction/auth_required/comment_video/')
def comment_video(request: Request, comment: schemas.CommentRequest):
    video_id = comment.video_id
    content = comment.content

    # constraints
    if not is_valid_uuid(video_id):
        return JsonResponse(error=f"{video_id} is not a valid ID")
    if len(content) > 200:
        return JsonResponse(error=f"The max limit for comment is 200 words.")

    try:
        user_id = request.headers.get('X-User-ID')
    except:
        return JsonResponse(error="Request not authorized", status=401)

    try:
        mq.publish({"event": "comment", "video_id": video_id, "user_id": user_id, "content": content}, EVENTS_QUEUE)
    except:
        return JsonResponse(error="Could not update database", status=500)
    
    return JsonResponse(status=200)

@app.post('/interaction/auth_required/subscribe/{channel_id}/')
def subscribe_channel(request: Request, channel_id: str):
    if not is_valid_uuid(channel_id):
        return JsonResponse(error=f"{channel_id} is not a valid ID.")
   
    try:
        user_id = request.headers.get('X-User-ID')
    except:
        return JsonResponse(error="Request not authorized", status=401)
       
    try:
        message = {
            "event": "subscribe",
            "user_id": str(user_id),
            "channel_id": str(channel_id)
        }
        mq.publish(message, EVENTS_QUEUE)
    except:
        return JsonResponse(error="Could not update database", status=500)

@app.post('/interaction/auth_required/unsubscribe/{channel_id}/')
def unsubscribe_channel(request: Request, channel_id: str):
    if not is_valid_uuid(channel_id):
        return JsonResponse(error=f"{channel_id} is not a valid ID.")
   
    try:
        user_id = request.headers.get('X-User-ID')
    except:
        return JsonResponse(error="Request not authorized", status=401)
       
    try:
        mq.publish({'event': 'unsubscribe', 'user_id': user_id, 'channel_id': channel_id}, EVENTS_QUEUE)
    except:
        return JsonResponse(error="Could not update database", status=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
    
