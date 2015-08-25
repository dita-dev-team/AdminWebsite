from flask import Flask
from flask_wtf import CsrfProtect
from flask.ext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dita Admin'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/dita'
CsrfProtect(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
db.create_all()

import api.views