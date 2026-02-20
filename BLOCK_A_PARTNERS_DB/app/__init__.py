from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint('main', __name__)
db = SQLAlchemy()
