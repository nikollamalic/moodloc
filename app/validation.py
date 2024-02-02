from functools import wraps
from flask import request, Response
from datetime import datetime

import app.exceptions as ex
import re

email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

# Decorator for user registration.
def validate_user_input(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        body = request.json
        try:
            if len(body['name']) < 4 or len(body['name']) > 64: 
                return Response("Invalid length for name: Must be between 4 and 64 characters long", 422)

            if len(body['password']) < 4 or len(body['password']) > 64: 
                return Response("Invalid length for password: Must be between 4 and 64 characters long", 422)
            
            if re.search(email_regex, body['email']) is None: 
                return Response("Wrong email address.", 422)

            if (datetime.utcnow() - datetime.strptime(body['birth_date'], "%Y-%m-%d")).days / 365 < 18.00: 
                return Response("User must be older than 18.")
        except KeyError as err: 
            return Response(f"Missing field: {err}", 422)
        except ValueError as err : 
            return Response(f"Incorrect input for {err}", 422)

        return f(*args, **kwargs)
    return decorated_function

# Prevent trash files from being added.
def validate_file_extension(filename):
    allowed_extensions = { "png", "jpg", "jpeg" }
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions