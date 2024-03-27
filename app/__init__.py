from flask import Flask # Import the Flask class from the flask module
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


# Create an instance of Flask called app which will be the central object
app = Flask(__name__)
#set config for the app
app.config.from_object(Config)

# creatae an instance of SQLAlchemy called db which will be the central object for our database
db = SQLAlchemy(app)
# set the config for the app
migrate = Migrate(app, db)


# import the routes to the app and also the models
from . import routes, models