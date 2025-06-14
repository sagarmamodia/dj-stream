# Introduction
DjStream is a video streaming platform that allows users to share videos and watch videos shared by other users. Users can upload videos, create channels, create playlists, search videos and get personalized video recommendations among other things. It uses modern development practices of **microservices**, **message queues** etc to enhance maintainability and scalability.

# Architecture

The application consist of multiple services (in a normal microservices fashion)
1. API Gateway
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
  
The diagramatic representation of the architecture of entire backend application
![image](https://github.com/user-attachments/assets/b1729eac-dc84-4821-a69a-4afc9949d80b)
