WTF_CSRF_ENABLED = True
SECRET_KEY = '9271104095808765503900460536960'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') #goodbye sqlite
SQLALCHEMY_DATABASE_URI = "postgresql://localhost/mutualassureddestruction_dev"
SQLALCHEMY_TRACK_MODIFICATIONS = False
