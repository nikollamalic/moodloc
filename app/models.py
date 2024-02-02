from app import db
from datetime import datetime

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique = True)
    birth_date = db.Column(db.DateTime)
    password_hash = db.Column(db.String(128))
    isActive = db.Column(db.Boolean, default = True)

# User defined locations.
class Place(db.Model):
    place_id = db.Column(db.Integer, primary_key = True)
    name =  db.Column(db.String(64))
    coordinates =  db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default = True)

    # References user table.
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

class Capture(db.Model) : 
    id = db.Column(db.Integer, primary_key = True)
    location_name = db.Column(db.String( 256 ))
    mood = db.Column(db.String(64))
    coordinates = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime,  default = datetime.utcnow)

    # References user table. 
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))