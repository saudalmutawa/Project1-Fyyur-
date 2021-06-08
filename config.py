import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:9048@localhost:5432/fyyur'

class DatabaseURI:

    # Just change the names of your database and crendtials and all to connect to your local system
    DATABASE_NAME = "fyyur"
    username = 'postgres'
    password = '9048'
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)
