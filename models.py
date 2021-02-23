
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import ARRAY

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

class Shows(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
      venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
      start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False, unique=True)
    genres = db.Column(ARRAY(db.String()), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    image_link = db.Column(db.String(500), nullable=False, unique=True)
    facebook_link = db.Column(db.String(120), nullable=False, unique=True)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.Text, default='We are on the lookout for a local artist to play every two weeks. Please call us.')
    createdAt = db.Column(db.DateTime)
    artists = db.relationship('Shows', backref = 'venue')
  


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column(ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, unique=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text, default = 'Looking for shows to perform at in the San Francisco Bay Area!')
    createdAt = db.Column(db.DateTime)
    songs = db.Column((ARRAY(db.String())))
    venues = db.relationship('Shows', backref = 'artist')