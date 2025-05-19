from django.urls import path
from . import views

urlpatterns = [
    path('auth/oauth/auth-url/', views.get_oauth2_url, name='auth-url'),
    path('auth/accounts/google/login/callback/', views.oauth_callback, name='google-oauth-callback'),
    path('auth/authenticate/', views.authenticate_request, name='authenticate'), 
    path('auth/renew-token/', views.renew_jwt_token, name='renew-token'),
    path('auth/email-auth/register/', views.register_user, name='register-user'),
    path('auth/email-auth/login/', views.login_user, name='login-user')
]
