import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    IMAGES_FOLDER = os.path.join(basedir, 'image_uploads')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False