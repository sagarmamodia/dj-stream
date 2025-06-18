# Endpoints 

## auth_service
- GET auth/oauth/auth-url/
  - get oauth url
  - Response format
  ```
  auth_url: <value>
  ```
- POST auth/authenticate/
  - used by api-gateway to authenticate requests having JWT token in Bearer header
- POST auth/renew-token/
  - renew jwt access token with your refresh token
  - Expected JSON format
    ```
    {
    access_token: <value>,
    refresh_token: <value>
    }
    ```
- POST auth/email-auth/register/
  - create an account with email
  - Expected JSON format
   ```
    {
    name: <value>,
    email:<value>,
    password: <value>
    }
    ```
- POST auth/email-auth/login/
  - login with email and password
  - Expected JSON format
  ```
  email: <value>,
  password: <value>
  ```

## channel_service
- GET channel/info/<channel_id>/
  - get all the information about a channel
  - Response format
  ```
  {
  id: <value>,
  name: <value>,
  description: <value>,
  user_id: <value>,
  created_at: <value>
  }
  ```
  
- GET channel/user/get_channels/<user_id>/
  - get all the channels that belongs to the user with id <user_id>
  - Response format
  ```
  {
    channels: [
      {
          id: <value>,
          name: <value>,
          description: <value>,
          user_id: <value>,
          created_at: <value>
      },
      {
        ...
      },
    ]
  }
  ```
  
- GET channel/video/get_all/<channel_id>/
  - get all the videos of a channel
  - Response format
  ```
  {
    videos: [
      {
          id: <value>,
          channel_id: <value>,
          title: <value>,
          description: <value>,
          file_id: <value>
      },
      {
        ...
      },
    ]
  }
  ```
  
- GET channel/playlist/get_all/<channel_id>/
  - get all the playlists of a channel
  - Response format
  ```
  {
    playlists: [
      {
          id: <value>,
          name: <value>,
          description: <value>,
          created_at: <value>
      },
      {
        ...
      },
    ]
  }
  ```
  
- GET channel/playlist/info/<playlist_id>/
  - get all the information about a playlist
  - Response format
  ```
  {
    id: <value>,
    channel_id: <value>,
    name: <value>,
    description: <value>,
    created_at: <value>
  }
  ```
  
- GET channel/playlist/get_videos/<playlist_id>/
  - get all the videos of a playlist
  - Response format
  ```
   {
    videos: [
      {
          id: <value>,
          channel_id: <value>,
          title: <value>,
          description: <value>,
          file_id: <value>
      },
      {
        ...
      },
    ]
  }
  ```
  
- POST channel/auth_required/create/
  - create a channel
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    name: <value>,
    description: <value>
  }
  ```
  - Response format
  ```
  {
    id: <value>
  }
  ```
  
- POST channel/auth_required/playlist/create/
  - create a playlist
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    channel_id: <value>,
    name: <value>,
    description: <value>
  }
  ```
  - Response format
  ```
  {
    id: <value>
  }
  ```

- POST channel/auth_required/playlist/add_video/
  - add a video in playlist
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    playlist_id: <value>,
    video_id: <value>
  }
  ```
  - Response format
  ```
  {
    status: <value>
  }
  ```

- POST channel/auth_required/playlist/remove_video/
  - remove a video in playlist
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    playlist_id: <value>,
    video_id: <value>
  }
  ```
  - Response format
  ```
  {
    status: <value>
  }
  ```
  
- POST channel/auth_required/video/upload_metadata/
  - Upload video-metadata such as title, description, etc after a video file has been successfully uploaded.
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    channel_id: <value>,
    title: <value>,
    description: <value>,
    public: <value>,
    file_id: <value>,
  }
  ```
  - Response format
  ```
  {
    id: <value>
  }
  ```

## video_service
- POST video/upload/initate/
  - request creation of an upload session
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    filename: <value>,
    chunk_size: <value>,
    total_chunks: <value>,
  }
  ```
  - Response format
  ```
  {
    upload_session_id: <value>
  }
  ```

- POST video/upload/chunk/
  - upload a chunk
  - This request requires the data in multipart/format-data
  - **requires access token in Bearer header**
  - Expected fields
  ```
  upload_id: <value>,
  filename: <value>,
  chunk_number: <value>,
  file: <byte_data>,
  ```
  - Response format
  ```
  {
    result: 'success'
  }
  ```
  
- POST video/upload/complete/
  - After all the chunks have been uploaded request the merging of all the chunks and a file_id of the uploaded file.
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    upload_session_id: <value>
  }
  ```
  - Response format
  ```
  {
    file_id: <value>
  }
  ```
- GET video/stream/<file_id>/
  - request video with file_id as a streaming response.
  - The range headers must be valid
  - It returns the data of video file in chunks of 64 KB with response headers
  ```
  Content-Type: <value>,
  Accept-Ranges: bytes,
  Content-Length: <value>,
  Content-Range: <value>
  ```

## interaction_service
- POST interaction/auth_required/add_like/<video_id>/
  - like a video with id <video_id>
  - **requires access token in Bearer header**

- POST interaction/auth_required/remove_like/<video_id>/
  - remove like from a video with id <video_id>
  - **requires access token in Bearer header**

- POST interaction/auth_required/add_dislike/<video_id>/
  - dislike a video with id <video_id>
  - **requires access token in Bearer header**

- POST interaction/auth_required/remove_dislike/<video_id>/
  - remove dislike from a video with id <video_id>
  - **requires access token in Bearer header**

- POST interaction/auth_required/subscribe/<channel_id>/
  - subscribe a channel with id <channel_id>
  - **requires access token in Bearer header**

- POST interaction/auth_required/unsubscribe/<channel_id>/
  - unsubscribe a channel with id <channel_id>
  - **requires access token in Bearer header**

- POST interaction/auth_required/comment_video/
  - add a comment on a video
  - **requires access token in Bearer header**
  - Expected JSON format
  ```
  {
    video_id: <value>,
    content: <value>
  }
  ```
