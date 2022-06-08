#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# app.config.from_object('config')
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete="CASCADE"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete="CASCADE"), nullable=False)

  def __repr__(self):
    return f'<Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  facebook_link = db.Column(db.String(120))
  address = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.String(120), nullable=False)
  image_link = db.Column(db.String(500))
  website = db.Column(db.String(500))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String)
  shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete-orphan')

  def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  image_link = db.Column(db.String(500))
  website = db.Column(db.String(500))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String)
  facebook_link = db.Column(db.String(120))
  shows = db.relationship('Show', backref='artist', lazy=True, cascade='all, delete-orphan')


with app.app_context():
  db.create_all()
