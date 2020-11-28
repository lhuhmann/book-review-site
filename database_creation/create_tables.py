import sys
from flask import Flask, render_template, request

from models import *
# add the folder containing connect.py to the python path
sys.path.append("..")
from connect import db_uri # pylint disable=import-error

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def create_tables():
  '''Creates the database tables defined in models.py'''
  db.create_all()

if __name__ == "__main__":
  with app.app_context():
    create_tables()
