# Introduction
DjStream is a video streaming platform that allows users to share videos and watch videos shared by other users. Users can upload videos, create channels, create playlists, search videos and get personalized video recommendations among other things. It uses modern development practices of **microservices**, **message queues** etc to enhance maintainability and scalability.

# Run locally
DjStream consists of a lot of moving parts and dependencies therefore it has been containerized for easy portability. You only need to install docker and docker-compose in your machine to run DjStream. 
After cloning the repo and installing docker and docker-compose run the following command to start the application: 
```
docker-compose up -d --build
```
This will run all the services(including postgres, mongodb, redis and rabbitmq) inside docker containers and expose the port 80 of API Gateway. The application is therefore running at ```localhost:80/```.

To start the application without rebuilding the containers use the following command:
```
docker-compose start
```
To stop the application and remove the containers use the following command:
```
docker-compose down
```
To just stop the application but keep the containers use the following command:
```
docker-compose stop
```

# Architecture

The application consist of multiple services (in a normal microservices fashion)
1. Auth Service
   - It provides login, account registration, OAuth, JWTAuthentication services. API Gateway uses this service to authenticate requests before forwarding requests to intended services.
2. Channel Service
   - It provides all the channel related functionalities for example channel creation, playlist creation, adding video to playlist, etc
3. Video Service
   - DjStream implements a resumable uploading process and VideoService handles the uploading and streaming part.
4. Interaction Service
   - DjStream allows users to like, dislike or comment on videos among other functionalities. This type of interactions are handled by the InteractionService in highly efficient manner.
   - It uses a message queue behind the scenes - pushes message to the queue which is then consumed by a consumer to update the database.
   - If the interaction requires the target user to be notified then a message is pushed to notifications-queue which is consumed by the notification system downstream.
5. Notification Service
   - It handled the websocket connection with clients and sending messages it picks up from the notifications-queue to the users over their websocket connection.
   - It uses Redis to implement fan-out architecture to ensure that all the processes of NotificationService receive the message since a user's websocket object could be in anyone of those processes.
6. API Gateway
   - API gateway is the entrypoint to the application - it act as a load balancer and reverse proxy and forward incoming requests to the correct service.
  
The diagramatic representation of the architecture of entire backend application:  

![image](https://github.com/user-attachments/assets/b1729eac-dc84-4821-a69a-4afc9949d80b)

# Database Schema 
DjStream uses Postgres for relational database - it stores likes, videos metadata, user account info, etc and MongoDB for video and image files

The following diagram depicts the database schema - tables and relationships among them:
 
![image](https://github.com/user-attachments/assets/94f7a738-2577-471b-8e3a-45bbeaa9b4e9)

# Further Improvements
1. Implement caching to reduce latency of response
2. Add video tracking functionality to track users behaviors and their watch history - this will be important for recommendation service.
3. Add a recommendation service
