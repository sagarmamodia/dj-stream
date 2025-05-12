from django.contrib import admin
from .models import User, OAuthToken, JwtRefreshToken

admin.site.register(User)
admin.site.register(OAuthToken)
admin.site.register(JwtRefreshToken)
