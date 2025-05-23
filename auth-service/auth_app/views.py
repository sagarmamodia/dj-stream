from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import secrets
import urllib
import requests
import os
from django.conf import settings
from django.http import JsonResponse
from . import jwt_auth
from .models import User, OAuthToken, JwtRefreshToken, AuthTypes
import json
import uuid

load_dotenv()

def get_oauth2_url(request):
    state = secrets.token_urlsafe(32) 
    request.session['oauth_state'] = state #store in backend session db for validation later

    #construct the oauth url
    params = {
            'client_id': os.getenv('GOOGLE_OAUTH_CLIENT'),
            
            #This should be the url of frontend not backend
            'redirect_uri': f"{settings.BACKEND_URL}/auth/accounts/google/login/callback/",
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'online',
            }
   
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    return JsonResponse({"auth_url": auth_url})

def oauth_callback(request):
   
    if request.GET.get('state') != request.session.pop('oauth_state', None):
        return JsonResponse({'err': 'Invalid State'}, status=400) # This should be a JSON response

    code = request.GET.get('code')
    token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data = {
                'code': code,
                'client_id': os.getenv('GOOGLE_OAUTH_CLIENT'),
                'client_secret': os.getenv('GOOGLE_OAUTH_SECRET'),
                'redirect_uri': f"{settings.BACKEND_URL}/auth/accounts/google/login/callback/",
                'grant_type': 'authorization_code',
                }
            ).json()
    
    access_token=token_response['access_token']
    # refresh_token = token_response['refresh_token']

    user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={'Authorization': f"Bearer {access_token}"}
            ).json()
  
    user = User.objects.filter(email=user_info['email']).first()
    if(user is None):
        user = User.objects.create(auth_type=AuthTypes.OAUTH.value, name=user_info['name'], email=user_info['email'])

    jwt_access_token, jwt_refresh_token = jwt_auth.generate_jwt_token(str(user.id), user.email, user.name)
   
    try:
        oauth_token_object, created = OAuthToken.objects.get_or_create(user=user)
        oauth_token_object.access_token = access_token
        # oauth_token_object.refresh_token = refresh_token
        oauth_token_object.save()
    except:
        return JsonResponse({"error": "Failure to put oauth tokens to database"}, status=500)
        
    try:
        jwt_refresh_token_object, created = JwtRefreshToken.objects.get_or_create(user=user)
        jwt_refresh_token_object.refresh_token = jwt_refresh_token 
        jwt_refresh_token_object.save()
    except:
        return JsonResponse({"error": "Failure to put jwt token to database"}, status=500)

    return JsonResponse({
        'access_token': jwt_access_token,
        'refresh_token': jwt_refresh_token_object.refresh_token,
        'user_info': {'email': user.email, 'name': user.name}
        })


def authenticate_request(request):
    
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        jwt_access_token = auth_header.split()[1]
    except:
        return JsonResponse({'err': 'Incorrect authorization header'}, status=501)
    
    user_data, expired = jwt_auth.verify_jwt_token(jwt_access_token)
    if(expired):
        return JsonResponse({'error': 'token expired'}, status=401)
    
    if(user_data is None):
        return JsonResponse({'error': 'Invalid token'}, status=401)
    
    response = JsonResponse({'status': 'valid'}, status=200)
    response['X-user-id'] = user_data['id']
    response['X-email'] = user_data['email']
    response['X-name'] = user_data['name'] 
    return response

@csrf_exempt
def renew_jwt_token(request):
    """
    Post request data format
    {
        access_token: str,
        refresh_token: str
    }

    Response format
    {
        access_token: str,
        refresh_token: str,
    }
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        jwt_access_token = data['access_token']
        jwt_refresh_token = data['refresh_token']

        user_data, expired = jwt_auth.verify_jwt_token(jwt_access_token)
        if(user_data is None):
            return JsonResponse({'error': 'Invalid access token'}, status=401)
        
        user_id = uuid.UUID(user_data['id'])
        actual_refresh_token_object = JwtRefreshToken.objects.filter(user__id=user_id).first()
        if(actual_refresh_token_object is None):
            return JsonResponse({"error": "No refresh token exists"}, status=400)

        if(jwt_refresh_token != actual_refresh_token_object.refresh_token):
            return JsonResponse({'error': 'Invalid refresh token'}, status=401)
        
        renewed_jwt_token, renewed_refresh_token = jwt_auth.generate_jwt_token(user_data['id'], user_data['email'], user_data['name'])
        
        #save new refresh token to database
        try:
            actual_refresh_token_object.refresh_token = renewed_refresh_token
            actual_refresh_token_object.save()
        except:
            return JsonResponse({"error": "Failure to save refresh token to database."}, status=500)

        return JsonResponse({'access_token': renewed_jwt_token, 'refresh_token': renewed_refresh_token}, status=200)
    
    else:
        return JsonResponse({'error': 'Only post requests are allowed'}, status=401)

@csrf_exempt
def register_user(request):
    """
    Post request data format
    {
        name: ,
        email: ,
        password: ,
    }

    Response data format
    {
        'status': 'success'
    }
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.create(auth_type=AuthTypes.EMAIL.value, name=name, email=email, password=password)
        except:
            return JsonResponse({"error": "Failure to create user in database."}, status=500)
        
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'error': 'Only post requests are allowed'}, status=401)

@csrf_exempt
def login_user(request):
    """
    Post request data format
    {
        name:,
        email:,
        password:,
    }

    Response data format
    {
        'access_token': ,
        'refresh_token':,
    }
    """
    
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.filter(email=email).first()
        except:
            return JsonResponse({"error": "Failure to fetch user from database"}, status=500)

        if(user.password != password):
            return JsonResponse({'error': 'Incorrect password'}, status=401)
    
        jwt_access_token, jwt_refresh_token = jwt_auth.generate_jwt_token(str(user.id), user.email, user.name)

        jwt_refresh_token_object = JwtRefreshToken.objects.filter(user=user).first()
        if(jwt_refresh_token_object is None):
            JwtRefreshToken.objects.create(user=user, refresh_token=jwt_refresh_token)
        else:
            try:            
                jwt_refresh_token_object.refresh_token = jwt_refresh_token
                jwt_refresh_token_object.save()
            except:
                return JsonResponse({"error": "Failure to save refresh token to database."}, status=500)
        
        return JsonResponse({'access_token': jwt_access_token, 'refresh_token': jwt_refresh_token}, status=200)
    
    else:
        return JsonResponse({'error': 'Only post requests are allowed'}, status=401)

