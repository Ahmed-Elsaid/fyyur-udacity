#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import ARRAY

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.order_by(Artist.createdAt.asc()).limit(10).all()
  venues = Venue.query.order_by(Venue.createdAt.asc()).limit(10).all()
  return render_template('pages/home.html', artists = artists, venues = venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  all_venues = Venue.query.distinct(Venue.city).all()
  def isThereUpcomingShow(all_data):
        shows = []
        for data in all_data:
              shows.append({
                'id':data.id,
                'name':data.name,
                'num_upcoming_shows': len(Shows.query.filter(Shows.start_time > datetime.now()).\
                  filter(Shows.venue_id == data.id).all())
              })
        return shows
  data = []
  for venue in all_venues:
        data.append({
          "city":venue.city,
          "state":venue.state,
          "venues":isThereUpcomingShow(Venue.query.filter(Venue.city == venue.city).all())
        })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for venue in venues:
        data.append({
          'id':venue.id,
          'name':venue.name,
          'num_upcoming_shows':len(Shows.query.filter(Shows.venue_id == venue.id).\
            filter(Shows.start_time > datetime.now()).all())
        })
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue:
        return render_template('errors/404.html'), 404
  upcomingShows = Shows.query.filter(Shows.venue_id == venue.id).filter(Shows.start_time > datetime.now()).all()
  pastShows = Shows.query.filter(Shows.venue_id == venue.id).filter(Shows.start_time < datetime.now()).all()
  def displayShows(shows):
        shows_data = []
        for show in shows:
              if show.artist:
                shows_data.append({
                  "artist_id": show.artist.id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": str(show.start_time)
                })
        return shows_data
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description" : venue.seeking_description if venue.seeking_talent else '',
    "image_link": venue.image_link,
    "past_shows":displayShows(pastShows),
    "upcoming_shows": displayShows(upcomingShows),
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  venue_name = None
  try:
    new_venue_data = request.get_json()
    venue_name = new_venue_data['name']
    venue = Venue(
      name = new_venue_data['name'],
      genres = new_venue_data['genres'],
      city = new_venue_data['city'],
      state = new_venue_data['state'],
      address = new_venue_data['address'],
      phone = new_venue_data['phone'],
      image_link = new_venue_data['image_link'],
      facebook_link = new_venue_data['facebook_link'],
      website = new_venue_data['website'],
      seeking_talent = new_venue_data['seeking_talent'],
      seeking_description = new_venue_data['seeking_description'],
      createdAt = datetime.now()
    )
    db.session.add(venue)
    db.session.commit()
  except :
      db.session.rollback()
      print(sys.exc_info())
      error = True
  finally:
    db.session.close()
  if not error:
      return jsonify({'message': f'Venue {venue_name} was successfully listed!'})
  else:
      return jsonify({'message': f'An error occurred {venue_name} could not be listed.'})

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  venue_name = None
  try:
      venue = Venue.query.get(venue_id)
      venue_name = venue.name
      db.session.delete(venue)
      db.session.commit()
  except :
      db.session.rollback()
      error = True
  finally:
    db.session.close()
  if not error:
        return jsonify({'message':f'Venue {venue_name} has been deleted'})
  else:
        return jsonify({'message':f' An error ocurred, Please Try again'})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  all_artists = Artist.query.all()
  for artist in all_artists:
        data.append({
          'id':artist.id,
          'name':artist.name
        })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  print(search_term)
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  for artist in artists:
        data.append({
          'id':artist.id,
          'name':artist.name,
          'num_upcoming_shows':len(Shows.query.filter(Shows.artist_id == artist.id).\
            filter(Shows.start_time > datetime.now()).all())
        })
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist:
        return render_template('errors/404.html'), 404
  upcoming_shows = Shows.query.filter(Shows.artist_id == artist.id).filter(Shows.start_time > datetime.now()).all()
  past_shows = Shows.query.filter(Shows.artist_id == artist.id).filter(Shows.start_time < datetime.now()).all()
  def displayShows(shows):
        shows_data = []
        for show in shows:
              if show.venue:
                shows_data.append({
                  "venue_id": show.venue.id,
                  "venue_name": show.venue.name,
                  "venue_image_link": show.venue.image_link,
                  "start_time": str(show.start_time)
                })
        return shows_data
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description if artist.seeking_venue else '',
    "image_link": artist.image_link,
    "songs": artist.songs or [],
    "past_shows": displayShows(past_shows),
    "upcoming_shows": displayShows(upcoming_shows),
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  print(upcoming_shows)
  print(past_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist.songs == None:
        artist.songs = []
  artist.songs = ','.join(artist.songs)
  if not artist:
        return render_template('errors/404.html'), 404
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  newArtistData = request.get_json()
  artist = Artist.query.get(artist_id)
  error = False
  try:
    for data in newArtistData:
        setattr(artist, data, newArtistData[data])
    db.session.commit()
  except :
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
        return jsonify({'message':'Artist has been updated'})
  else:
        return jsonify({'message': f'An error occurred {artist.name} could not be updated.'})

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue:
        return render_template('errors/404.html'), 404
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  newVenueData = request.get_json()
  venue = Venue.query.get(venue_id)
  error = False
  try:
    for data in newVenueData:
        setattr(venue, data, newVenueData[data])
    db.session.commit()
  except :
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
        return jsonify({'message':'Venue has been updated'})
  else:
        return jsonify({'message': f'An error occurred {venue.name} could not be updated.'})

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  new_artist_data = request.get_json()
  error = False
  artist_name = None
  try:
    new_artist_data = request.get_json()
    artist_name = new_artist_data['name']
    artist = Artist(
      name = new_artist_data['name'],
      city = new_artist_data['city'],
      state = new_artist_data['state'],
      phone = new_artist_data['phone'],
      genres = new_artist_data['genres'],
      image_link = new_artist_data['image_link'],
      facebook_link = new_artist_data['facebook_link'],
      website = new_artist_data['website'],
      seeking_venue = new_artist_data['seeking_venue'],
      seeking_description = new_artist_data['seeking_description'],
      songs = new_artist_data['songs'] or [],
      createdAt = datetime.now()
    )
    db.session.add(artist)
    db.session.commit()
  except :
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
      return jsonify({'message': f'Artist {artist_name} was successfully listed!'})
  else:
      return jsonify({'message': f'An error occurred {artist_name} could not be listed.'})

# Delete Artist
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  artist_name = None
  try:
      artist = Artist.query.get(artist_id)
      artist_name = artist.name
      db.session.delete(artist)
      db.session.commit()
  except :
      db.session.rollback()
      error = True
  finally:
    db.session.close()
  if not error:
        return jsonify({'message':f'Artist {artist_name} has been deleted'})
  else:
        return jsonify({'message':f' An error ocurred, Please Try again'})

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows_data = db.session.query(Shows, Artist, Venue).join(Artist).join(Venue).all()
  for show in shows_data:
        data.append({
          "venue_id": show.Venue.id,
          "venue_name": show.Venue.name,
          "artist_id": show.Artist.id,
          "artist_name": show.Artist.name,
          "artist_image_link": show.Artist.image_link,
          "start_time": str(show.Shows.start_time)
        })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    new_show_data = request.get_json()
    artist_id = new_show_data['artist_id']
    venue_id = new_show_data['venue_id']
    start_time = new_show_data['start_time']
    newShow = Shows(artist_id = artist_id, venue_id = venue_id, start_time =start_time)
    db.session.add(newShow)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    return jsonify({'message':'Show was successfully listed!'})
  else:
    return jsonify({'message':'An error occurred. Show could not be listed.'})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
