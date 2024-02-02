import jwt 
from datetime import datetime
from functools import wraps
from flask import request, Response

# Very safe secrets.
secret = "verysafe"
issuer = "mood_auth"

def authorize(f):
    """
    Authorization Decorator.

    Get JWT from authorization header and decypher it.
    Pass 'user_id' to any decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token is None:
            return Response("Authorization has been denied!", 401)
        
        auth_service = Authorize()
        try :
            decoded_jwt = auth_service.decode(token.replace('Bearer ', ''))
            kwargs['user_id'] = decoded_jwt['user_id']
            if auth_service.has_expired(decoded_jwt) :
                return Response("Authorization has been denied!", 401)
        except: 
            return Response("Authorization has been denied!", 401)
        return f(*args, **kwargs)
    return decorated_function

class Claim : 
    """
    JSON payload of JWT token.
    """
    def __init__(self, user_id): 
        self.iss = issuer
        self.exp = int(datetime.utcnow().timestamp()) + 5400
        self.user_id = user_id
    
    def to_dict(self): 
        return {
            'iss' : self.iss,
            'exp' : self.exp,
            'user_id' : self.user_id
        }

class Authorize : 
    """
    Authorization Service.

    Contains main utilities for managing JWT token.
    """
    def encode(self, user_id):
        return jwt.encode(Claim(user_id).to_dict(), secret, algorithm="HS256")

    def decode(self, token):
        return jwt.decode(token, secret, algorithms=['HS256'])

    def has_expired(self, token):
        return int(token['exp']) < int(datetime.utcnow().timestamp())