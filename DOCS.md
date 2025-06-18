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
    channel_list: [
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
- GET channel/info/<channel_id>/
  - get all the information about a channel
   - Response format
  ```
  id: <value>,
  name: <value>,
  description: <value>,
  user_id: <value>,
  created_at: <value>
  ```
- GET channel/info/<channel_id>/
  - get all the information about a channel
   - Response format
  ```
  id: <value>,
  name: <value>,
  description: <value>,
  user_id: <value>,
  created_at: <value>
  ```
- GET channel/info/<channel_id>/
  - get all the information about a channel
   - Response format
  ```
  id: <value>,
  name: <value>,
  description: <value>,
  user_id: <value>,
  created_at: <value>
  ```
