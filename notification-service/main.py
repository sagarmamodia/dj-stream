from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
import asyncio
from redis.asyncio import Redis
import requests
import json

AUTH_SERVICE = "http://localhost:8000/"

app = FastAPI()

connected_users: dict[str, WebSocket] = {}

REDIS_URL = 'redis://localhost:6379'
NOTIFICATIONS_CHANNEL = 'notifications'

redis = None 
pubsub = None

@app.websocket('/ws/{access_token}/')
async def websocket_endpoint(websocket: WebSocket, access_token: str):

    await websocket.accept()

    # authenticate token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f'{AUTH_SERVICE}/auth/authenticate/', headers=headers)
 
    if response.status_code == 401:
        await websocket.close(code=1008, reason="Invalid token")
        return 

    user_id = response.headers.get('X-User-ID')
    connected_users[user_id] = websocket 
    await websocket.send_text("Websocket connected.")
    print(f"User with {user_id} connected.")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        print("Client Disconnected.")

         
async def redis_listener():
    global redis, pubsub
    redis = Redis(host="localhost", port=6379, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe(NOTIFICATIONS_CHANNEL)
    
    while True:
        message = await pubsub.get_message()
        if message and message["type"] == "message":

            try:
                data = json.loads(message["data"])
                user_id = data["user_id"]
                payload = data["message"]

                websocket = connected_users.get(str(user_id))
                if websocket:
                    await websocket.send_text(payload)
                    print(f"Sent to user {user_id}: {payload}")

            except Exception as e:
                print("Error processing message:", e)

    asyncio.sleep(0.1)

# Start Redis listener on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_listener())


# Shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down Redis connections...")
    if pubsub:
        pubsub.close()   # Close PubSub connection
    if redis:
        redis.close()    # Close Redis client socket
        redis.connection_pool.disconnect()  # Extra cleanup for all pooled connections
    print("Redis cleanup complete.")













