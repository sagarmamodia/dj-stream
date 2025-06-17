# Endpoints 

## auth_service
- GET auth/oauth/auth-url/
  - get oauth url
- POST auth/authenticate/
  - used by api-gateway to authenticate requests having JWT token in Bearer header
- POST auth/renew-token/
  - renew jwt access token with your refresh token
  - Expected JSON format
    ```
    {
    access_token: <str>,
    refresh_token: <str>
    }
    ```
- POST auth/email-auth/register/
  - create an account with email
  - Expected JSON format
   ```
    {
    name: <str>,
    email: <str>,
    password: <str>
    }
    ```
