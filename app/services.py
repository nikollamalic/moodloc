from app.models import User, Place, Capture
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime
from enum import Enum
from sqlalchemy import func
from sqlalchemy import desc
from geopy.distance import geodesic

import re
import app.exceptions as ex

# GPS Coordinations regex pattern. 
gps_regex_pattern = "^([-+]?)([\d]{1,2})(((\.)(\d+)(,)))(\s*)(([-+]?)([\d]{1,3})((\.)(\d+))?)$"

class DefaultPlace(Enum):
    Home = 1,
    Work = 2,
    Lover = 3,
    Market = 4

class UserService : 
    """
    CRUD operations.

    @methods : [get_user(), check_login(), create_user()]
    """
    # Get user general information.
    def get_user(self, user_id):
        return User.query.filter_by(user_id = user_id).first()

    # Confirm user password and return matching user object.
    def check_login(self, email, password):
        user = User.query.filter_by(email = email).first()
        if user is None: 
            raise ex.NotFoundException("User not found.")
        check_password = check_password_hash(user.password_hash, password)
        if check_password is False:
            raise ex.InvalidPassword("Invalid password.")
        return user

    # Create new user with hashed password.
    def create_user(self, user, password):
        new_user = User(name = user['name'],
        email = user['email'],
        birth_date = datetime.strptime(user['birth_date'], "%Y-%m-%d"),
        password_hash = generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

class PlaceService:
    """
    CRUD operations.

    Create and read user places.
    """

    # Create a new place from the list of possible ones.
    def set_user_place(self, place: DefaultPlace, user_id, coords):
        options = [attr for attr in dir(DefaultPlace) if not attr.startswith('_')]
        if hasattr(DefaultPlace, place) is False: 
            raise ex.WrongOptionException(
            f"""Wrong input for enumerable DefaultPlace. 
                Options: {options}""")
        
        if re.search(gps_regex_pattern, coords) :
            places = db.session.query(Place).filter(Place.is_active == True, Place.name == place, Place.user_id == user_id).count()
            
            # Keep active only the latest places, this prevents user from having multiple homes, etc.
            if places > 0 : 
                db.session.query(Place).filter(Place.is_active == True, Place.name == place, Place.user_id == user_id).update({"is_active" : False})
                db.session.commit()

            new_place = Place(name = str(place), 
                            coordinates = coords,
                            user_id = user_id)
            db.session.add(new_place)
            db.session.commit()

        else : 
            raise ex.ValidationException("Validation failed for coordinates.")

    # Retrieve list of places that the user entered.
    def get_user_places(self, user_id): 
        places = db.session.query(Place).filter(Place.is_active == True, Place.user_id == user_id).all()
        places = [{ 'name' : place.name, 'coords': place.coordinates } for place in places]
        return places

class CaptureService:
    """ 
    CRUD operations, and data aggregations.

    Used for creating new captures and getting overall statistics.
    """

    def create_capture(self, mood, coordinates, user_id, address):
        capture = Capture(mood = mood, coordinates = coordinates, user_id = user_id, location_name = address)
        db.session.add(capture)
        db.session.commit()

    # Get percentage of each emotion for specific user.
    def get_emotion_distribution(self, user_id):
        emotion_distribution = db.session.query(Capture.mood, func.count(Capture.mood)).group_by(Capture.mood).filter(Capture.user_id == user_id).all()
        total_captures = 0
        for mood, occurence in emotion_distribution : 
            total_captures += occurence
        
        emotion_distribution_dict = dict(emotion_distribution)
        for key, value in emotion_distribution_dict.items() : 
            # Assign percentage values.
            emotion_distribution_dict[key] = f"{float('%.4f'%(value / total_captures * 100))} %"

        return emotion_distribution_dict

    # Get overtime emotional progress of the user. Useful for graph charts.
    def get_emotional_progress(self, user_id):
        emotional_progress = (db.session.query(Capture.location_name, Capture.mood, Capture.timestamp)
                            .filter(Capture.user_id == user_id)
                            .order_by(desc(Capture.timestamp)).all())

        emotional_progress_filtered = []
        for item in emotional_progress:
            # Prettify
            filtered = {
                'location_name': item.location_name,
                'mood': item.mood,
                'timestamp': item.timestamp 
            }
            emotional_progress_filtered.append(filtered)

        return emotional_progress_filtered

    # Return proximity to user defined locations on every "happy" capture.
    def get_happines_proximity(self, user_id):
        places = PlaceService().get_user_places(user_id)
        happy_captures = (db.session.query(Capture)
                                    .filter(Capture.user_id == user_id, Capture.mood == "happy")
                                    .order_by(desc(Capture.timestamp)).all())

        happy_spots = []
        for capture in happy_captures : 
            place_data = []
            min_prox = 0.0
            for place in places : 
                capture_coords = eval(capture.coordinates)
                place_coords = eval(place['coords'])
                proximity = geodesic(capture_coords, place_coords).kilometers
                place_data.append({'name' : place['name'], 'proximity' : proximity})

            happy_spots.append({
                'location_name' : capture.location_name,
                'timestamp' : capture.timestamp,
                'places' : place_data
            })

        return happy_spots