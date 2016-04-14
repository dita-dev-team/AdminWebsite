from flask import Flask
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_wtf import CsrfProtect
from flask.ext.bcrypt import Bcrypt

from api import config

app = Flask(__name__)
app.config.from_object(config)
CsrfProtect(app)
bcrypt = Bcrypt(app)

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)

import api.views
