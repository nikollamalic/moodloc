import os
from app import app
from flask import request, Response, jsonify
from auth.auth import Claim, Authorize, authorize
from app.services import UserService, PlaceService, CaptureService
from datetime import datetime
from app.validation import validate_user_input, validate_file_extension
from werkzeug.utils import secure_filename
from GPSPhoto import gpsphoto
from geopy.geocoders import Nominatim
from PIL import Image
from emotion_util.model import EMR
from numpy import array

import app.exceptions as ex
from sqlalchemy.exc import IntegrityError

emotion_recognition = EMR()
user_service = UserService()
auth = Authorize()

@app.route('/authorize', methods = ['POST'])
def request_jwt():
    """
    Get JWT token based on user credentials. 
    Token expires in 30 minutes.
    """
    try : 
        user = user_service.check_login(request.json['email'], request.json['password'])
    except KeyError as err : 
        return Response(f"Missing field: {err}", 422)
    except : 
        return Response("Authentication failed.", 401)

    encoded_jwt = auth.encode(user.user_id)
    return jsonify({"token" : str(encoded_jwt, "UTF-8")})

@app.route('/user')
@authorize
def get_user(*args, **kwargs):
    user = user_service.get_user(kwargs['user_id'])
    return jsonify({
        'name' : user.name,
        'email' : user.email,
        'age' : str(datetime.utcnow().year - user.birth_date.year)
    })

@app.route('/user', methods = ['POST'])
@validate_user_input
def create_user():
    try : 
        user_service.create_user(request.json, request.json['password'])
        return Response("User created", 201)
    except IntegrityError as err:
        return Response("User already exists", 409)

@app.route('/place', methods = ['POST'])
@authorize
def add_user_place(*args, **kwargs): 
    place_service = PlaceService()
    try : 
        place_service.set_user_place(
            place = request.json['place'],
            user_id = kwargs['user_id'],
            coords = request.json['coordinates']
        )
    except KeyError as err: 
        return Response(f"Missing field: {err}", 422)
    except ex.ValidationException as err:
        return Response(f"Error: {err}", 422)
    except ex.WrongOptionException as err: 
        return Response(f"Error: {err}", 422)
    return Response("Place added.", 201)

@app.route('/place', methods = ['GET'])
@authorize
def get_user_places(*args, **kwargs):
    place_service = PlaceService()
    places = place_service.get_user_places(kwargs['user_id'])
    return jsonify({ "total" : len(places), "places" : places })

@app.route('/capture', methods = ['POST'])
@authorize
def upload_capture(*args, **kwargs):
    """
    Analyze the photo to detect the mood and location.
    Save the output result to the database.
    """
    file = request.files['file']
    capture_service = CaptureService()
    if file and validate_file_extension(file.filename):
        # Process file.
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['IMAGES_FOLDER'], filename)
        file.save(file_path)

        # Get location from image metadata.
        data = gpsphoto.getGPSData(file_path)
        coords = f"{data['Latitude']}, {data['Longitude']}"
        geolocator = Nominatim(user_agent="mood_app")
        location = geolocator.reverse(coords)
        
        # Extract mood from image.
        mood = emotion_recognition.get_emotion(file_path)

        capture_service.create_capture(mood, coords, kwargs['user_id'], location.address)
        return Response('Uploaded successfully', 201)

    return Response("Something went wrong.", 500)

@app.route('/statistics/mood')
@authorize
def get_mood_distribution(*args, **kwargs) : 
    return jsonify(CaptureService().get_emotion_distribution(kwargs['user_id']))

@app.route('/statistics/state-of-mind')
@authorize
def get_state_of_mind(*args, **kwargs):
    return jsonify(CaptureService().get_emotional_progress(kwargs['user_id']))

@app.route('/statistics/happiness')
@authorize
def get_happiest_place(*args, **kwargs): 
    return jsonify(CaptureService().get_happines_proximity(kwargs['user_id']))
    