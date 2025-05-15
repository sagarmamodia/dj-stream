import jwt
from datetime import datetime, timezone, timedelta
from django.conf import settings

def generate_jwt_token(id, email, name):
    payload = {
            'id': id,
            'email': email,
            'name': name,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=30),
            'iat': datetime.now(timezone.utc),
        }
    jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    payload_for_refresh_token = {
                'jwt_token': jwt_token,
                'exp': datetime.now(timezone.utc) + timedelta(days=7),
                'iat': datetime.now(timezone.utc),
    }

    refresh_token = jwt.encode(payload_for_refresh_token, settings.SECRET_KEY, algorithm='HS256')
    return jwt_token, refresh_token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except:
        return None, False
    
    exp = payload.get('exp')
    exp = datetime.fromtimestamp(exp, tz=timezone.utc)
 
    if exp < datetime.now(timezone.utc):
        return None, True
    
    id = payload.get('id')
    email = payload.get('email')
    name = payload.get('name')
    user_data = {'id': id, 'email': email, 'name': name}

    return user_data, False
