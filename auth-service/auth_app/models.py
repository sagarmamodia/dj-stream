from django.db import models
import uuid

class AuthTypes(models.TextChoices):
    OAUTH = 'OAUTH', 'Oauth'
    EMAIL = 'EMAIL', 'E-mail'

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_type = models.CharField(choices=AuthTypes.choices)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OAuthToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class JwtRefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
# if __name__=='__main__':
#     user = User(auth_type='OAUTH', name='Sagar', email='sagar@gmail.com')
#     oauth = OAuthToken(user=user, access_token="32ds23rf")
#     jwt = JwtRefreshToken(user=user, refresh_token="wkh239hs")
