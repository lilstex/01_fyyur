#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import re
import sys
import dateutil.parser
import babel
from flask import abort, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from models import *
import logging
from logging import Formatter, FileHandler
from datetime import datetime
from forms import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  # Checking if the form passes validation
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_venue_submission'))
  
  # Formatting user input before adding to the db
  get_genres = form.genres.data
  genres = ", ".join(get_genres)

  try:
    error = False
    # Creating a new venue by inserting the venue data into the db
    new_venue = Venue(
      name=form.name.data, 
      city=form.city.data, 
      state=form.state.data, 
      address=form.address.data, 
      phone=form.phone.data,
      image_link=form.image_link.data,
      website=form.website_link.data, 
      facebook_link=form.facebook_link.data, 
      genres=genres,
      seeking_description = form.seeking_description.data, 
      seeking_talent=form.seeking_talent.data
      )
    db.session.add(new_venue)
    db.session.commit()
  except:
    # If an error occurs during insertion, set error to True
    error = True
    db.session.rollback()
  finally:
    # Close the session
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(500)


#  Get Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venues = Venue.query.order_by('id').all()
    city_state = set()
    for venue in venues:
      city_state.add((venue.state, venue.city))
    city_state_list = list(city_state)
    # city_state_list.sort(key=itemgetter(1,0))

    for location in city_state_list:
      venue_list = []
      for venue in venues:
       if (venue.state == location[0]) and (venue.city == location[1]):
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming_shows = 0
        for show in venue_shows:
          if show.start_time > datetime.now():
            num_upcoming_shows += 1

        venue_list.append({
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows": num_upcoming_shows
        })

      data.append({
        "state": location[0],
        "city": location[1],
        "venues": venue_list
        })
    return render_template('pages/venues.html', areas=data);


#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venues_list = []
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  for venue in venues:
    venue_show = Show.query.filter_by(venue_id=venue.id).all()
    num_upcoming_shows = 0
    for show in venue_show:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    venues_list.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  response={
    "count": len(venues),
    "data": venues_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


#  Show Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('venues'))
  upcoming_shows = []
  past_shows = []
  upcoming_shows_count = 0
  past_shows_count = 0
  for show in venue.shows:
    if show.start_time > datetime.now():
      upcoming_shows_count +=1
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
      past_shows_count +=1
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
      })
  
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": re.sub(',', '', venue.genres), # Removing the comma and replacing it with a space
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "address": venue.address,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  } 
  return render_template('pages/show_venue.html', venue=data)


#  Edit and Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form = VenueForm(formdata=None, obj=venue)
  if not venue:
        return redirect(url_for('venues'))

  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website_link": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))

  # Formatting user input before adding to the db
  get_genres = form.genres.data
  genres = ", ".join(get_genres)

  try:
    error = False
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.address = form.address.data
    venue.genres = genres
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    error = True
    print(f'An error occurred editing venue "{venue.name}"')
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash('An error occurred! Venue '+ form.name.data + ' could not be updated.')
    abort(500)


#  Delete Venues
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['GET','POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    print(venue.name)
    if not venue:
      return redirect(url_for('venues'))
    else:
      db.session.delete(venue)
      db.session.commit()
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred deleting venue.')
    abort(500)
  else:
    flash(f'Venue {venue.name} deleted successfully!')
    return redirect(url_for('venues'))
    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
   # Checking if the form passes validation
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_artist_submission'))

  # Formatting user input before adding to the db
  get_genres = form.genres.data
  genres = ", ".join(get_genres)

  try:
    error = False
    # Creating a new artist by inserting the artist data into the db
    new_artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = genres,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data 
      )
    db.session.add(new_artist)
    db.session.commit()
  except:
    # If an error occurs during insertion, set error to True
    error = True
    db.session.rollback()
  finally:
    # Close the session
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    abort(500)


@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  artists_list = []
  for artist in artists:
    artist_show = Show.query.filter_by(artist_id=artist.id).all()
    num_upcoming_shows = 0
    for show in artist_show:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    artists_list.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  response = {
    "count": len(artists),
    "data": artists_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  if not artist:
    return redirect(url_for('artists'))
  upcoming_shows = []
  past_shows = []
  upcoming_shows_count = 0
  past_shows_count = 0
  for show in artist.shows:
    if show.start_time > datetime.now():
      upcoming_shows_count +=1
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
      past_shows_count +=1
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
      })
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": re.sub(',', '', artist.genres), # Replacing the comma with a space
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  if not artist:
        return redirect(url_for('artists'))
  form = ArtistForm(formdata=None, obj=artist)

  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_artist_submission',artist_id=artist_id))
    
  # Formatting user input before adding to the db
  get_genres = form.genres.data
  genres = ", ".join(get_genres)

  try:
    error = False
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = genres
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('An error occurred! Artist '+ artist.name + ' could not be updated.')
    abort(500)


#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>/delete', methods=['GET', 'POST'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    artist = Artist.query.get(artist_id)
    if not artist:
      return redirect(url_for('artists'))
    else:
      db.session.delete(artist)
      db.session.commit()
  except:
    print(sys.exc_info())
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # flash(f'An error occurred deleting artist {artist.name}.')
    abort(500)
  else:
    flash(f'Artist {artist.name} deleted successfully!')
    return redirect(url_for('artists'))
    
  # BONUS CHALLENGE: Implement a button to delete a Artist on a Artist Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.order_by('id').all()
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
   # Checking if the form passes validation
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_show_submission'))
  try:
    error = False
    new_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
      )
    db.session.add(new_show)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
  # on successful db insert, flash success
    flash('Show was successfully listed!')  
    return render_template('pages/home.html')
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')     
    abort(500)
  

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
