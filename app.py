#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  flash,
  redirect,
  url_for,
  abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy 
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form
from forms import *
import time
from sqlalchemy import and_
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.DatabaseURI')
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

TEMPLATES_AUTO_RELOAD = True

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import Show, Venue, Artist
#models are in models.py


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

current_time=time.strftime('%Y-%m-%d %H:%S:%M',time.localtime(time.time()))


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data=[]
  for cities in db.session.query(Venue.state,Venue.city).distinct(Venue.city).all():#loop through distinct cities
    venueslist=[]
    rows = Venue.query.filter(Venue.city==cities.city).all()
    for row in rows:   #loop through venue objects 
      upcomingshows=Venue.query.join(Show).filter(and_(Show.venue_id==row.id , Show.start_time>current_time)).all()
      count=len(upcomingshows) #number of upcoming shows
      venueslist.append({
        "id":row.id,
        "name":row.name,
        "num_upcoming_shows":count
         })
    data.append({
      "city":cities.city,
      "state":cities.state,
      "venues":venueslist
    }
    )
 
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  resultt = request.form.get('search_term', '') #store search result
  
  query=Venue.query.filter(Venue.name.ilike('%'+resultt+'%')).all()  #search in database where there is a partial string from the result
  venuesdata=[]
  for row in query: #loop through venue objects 
    upcomingshows=db.session.query(Show,Venue).select_from(Venue).join(Show).filter(and_(Show.venue_id==row.id,Show.start_time>current_time)).all()
    count=len(upcomingshows)
    venuesdata.append({
      "id":row.id,
      "name":row.name,
      "num_upcoming_shows":count
    })
  response={
    "count":len(query),
    "data":venuesdata  
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
 
  query1 = Venue.query.get(venue_id)
  genrelist=query1.genres.split(",")
  upcomingshows=db.session.query(Show,Venue).select_from(Venue).join(Show).filter(and_(Show.venue_id==query1.id, Show.start_time>current_time)).all()
  countup=len(upcomingshows)
  pastshows=db.session.query(Show,Venue).select_from(Venue).join(Show).filter(and_(Show.venue_id==venue_id,Show.start_time<=current_time)).all()
  countpast=len(pastshows)
  past_list=[]
  up_list=[]
  for past in pastshows:
    id=past.Show.artist_id
    artistquery = Artist.query.get(id)
    past_list.append({
      "artist_id":artistquery.id,
      "artist_name":artistquery.name,
      "artist_image_link":artistquery.image_link,
      "start_time":past.Show.start_time
    })
  for up in upcomingshows:
    id1=up.Show.artist_id
    artistquery2 = Artist.query.get(id1)
    up_list.append({
      "artist_id":artistquery2.id,
      "artist_name":artistquery2.name,
      "artist_image_link":artistquery2.image_link,
      "start_time":up.Show.start_time
    })
  
  
  data = {
    "id":query1.id,
    "name":query1.name,
    "genres":genrelist,
    "address":query1.address,
    "city":query1.city,
    "state":query1.state,
    "phone":query1.phone,
    "website":query1.website,
    "facebook_link":query1.facebook_link,
    "seeking_talent":query1.seeking_talent,
    "seeking_description":query1.seeking_description,
    "image_link":query1.image_link,
     "past_shows": past_list,
     "upcoming_shows":up_list ,
     "past_shows_count": countpast,
    "upcoming_shows_count": countup,
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
  seeking=False
  if request.form.get("seeking_talent",False)=="y":
      seeking=True
  else:
    seeking=False
  form = VenueForm(request.form)
  try:
    if(form.validate()):

      venue_data=Venue(name=request.form['name'],city=request.form['city'],state=request.form['state'],address=request.form['address'],phone = request.form['phone'],genres=request.form['genres'],facebook_link=request.form['facebook_link'],image_link=request.form['image_link'],website=request.form['website_link'],seeking_talent=seeking,seeking_description=request.form['seeking_description'])
      form.populate_obj(venue_data)
      db.session.add(venue_data)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    data = Venue.query.filter(Venue.name==request.form['name'])
  except():
    db.session.rollback()
    print(sys.exc_info())

    flash('An error occurred. Venue ' + data.name + ' could not be listed.')

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete_venue', methods=['DELETE'])
def delete_venue(venue_id):

  
  error=False
  try:
    venue1=Venue.query.get(venue_id)
    db.session.delete(venue1)
    db.session.commit()
  except():
    db.session.rollback()
    print(sys.exc_info())
    error=True
  
  if error:
    abort(500)
  else:
    return render_template('pages/home.html')

  
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  rows = Artist.query.all()
  data=[]
  for row in rows:
    data.append({
      "id":row.id,
      "name":row.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
 
  result=request.form.get('search_term', '')
  rows = Artist.query.filter(Artist.name.ilike('%'+result+'%')).all()
  data=[]
  for row in rows:
    upcomingshows=db.session.query(Show,Artist).select_from(Artist).join(Show).filter(and_(Show.venue_id==Artist.id,Show.start_time>current_time)).all()
    data.append({
      "id":row.id,
      "name":row.name,
      "num_upcoming_shows":len(upcomingshows)
    })
  response={
    "count":len(rows),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  
  row=Artist.query.get(artist_id)
  genrelist = row.genres.split(",")
  pastshows=db.session.query(Show,Artist).select_from(Artist).join(Show).filter(and_(Show.artist_id==row.id, Show.start_time<=current_time)).all()
  upcomingshows=db.session.query(Show,Artist).select_from(Artist).join(Show).filter(and_(Show.artist_id==row.id, Show.start_time>current_time)).all()
  pastlist=[]
  uplist=[]
  for past in pastshows:
    venueinfo=Venue.query.get(past.Show.venue_id)
    pastlist.append({
      "venue_id":venueinfo.id,
      "venue_name":venueinfo.name,  
      "venue_image_link":venueinfo.image_link,
      "start_time":past.Show.start_time
    })
  for up in upcomingshows:
    venueinfo1=Venue.query.get(up.Show.venue_id)
    uplist.append({
      "venue_id":venueinfo1.id,
      "venue_name":venueinfo1.name,
      "venue_image_link":venueinfo1.image_link,
      "start_time":up.Show.start_time
    })
  
  data={
    "id": row.id,
    "name": row.name,
    "genres": genrelist,
    "city": row.city,
    "state": row.state,
    "phone": row.phone,
    "website": row.website,
    "facebook_link": row.facebook_link,
    "seeking_venue": row.seeking_venue,
    "seeking_description": row.seeking_description,
    "image_link": row.image_link,
    "past_shows": pastlist,
    "upcoming_shows":uplist,
    "past_shows_count": len(pastshows),
    "upcoming_shows_count": len(upcomingshows),
  }

  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artistinfo=Artist.query.get(artist_id)
  artist={
    "id": artist_id,
    "name": artistinfo.name,
    "genres": artistinfo.genres,
    "city": artistinfo.city,
    "state": artistinfo.state,
    "phone": artistinfo.phone,
    "website": artistinfo.website,
    "facebook_link": artistinfo.facebook_link,
    "seeking_venue": artistinfo.seeking_venue,
    "seeking_description": artistinfo.seeking_description,
    "image_link": artistinfo.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  seeking=False
  if request.form.get("seeking_venue",False)=="y":
      seeking=True
  else:
   seeking=False
  artist = Artist.query.get(artist_id)
  artist.name=request.form['name']
  artist.city=request.form['city']
  artist.genres=request.form['genres']
  artist.state=request.form['state']
  artist.phone=request.form['phone']
  artist.facebook_link=request.form['facebook_link']
  artist.image_link=request.form['image_link']
  artist.website=request.form['website_link']
  artist.seeking_venue=seeking
  artist.seeking_description=request.form['seeking_description']
  db.session.commit()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venueinfo=Venue.query.get(venue_id)
  venue={
    "id": venueinfo.id,
    "name": venueinfo.name,
    "genres": venueinfo.genres,
    "address": venueinfo.address,
    "city": venueinfo.city,
    "state": venueinfo.state,
    "phone": venueinfo.phone,
    "website": venueinfo.website,
    "facebook_link": venueinfo.facebook_link,
    "seeking_talent": venueinfo.seeking_talent,
    "seeking_description": venueinfo.seeking_description,
    "image_link":venueinfo.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  seeking=False
  if request.form.get("seeking_talent",False)=="y":
      seeking=True
  else:
   seeking=False
  venue = Venue.query.get(venue_id)
  venue.name=request.form['name']
  venue.city=request.form['city']
  venue.genres=request.form['genres']
  venue.state=request.form['state']
  venue.phone=request.form['phone']
  venue.facebook_link=request.form['facebook_link']
  venue.image_link=request.form['image_link']
  venue.website=request.form['website_link']
  venue.seeking_talent=seeking
  venue.seeking_description=request.form['seeking_description']
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  seeking=False
  if request.form.get("seeking_venue",False)=="y":
      seeking=True
  else:
   seeking=False
  form = ArtistForm(request.form)
  try:
    if(form.validation):
      artist_data=Artist(name=request.form['name'],city=request.form['city'],state=request.form['state'],phone = request.form['phone'],genres=request.form['genres'],facebook_link=request.form['facebook_link'],image_link=request.form['image_link'],website=request.form['website_link'],seeking_venue=seeking,seeking_description=request.form['seeking_description'])
      form.populate_obj(artist_data)
      db.session.add(artist_data)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    data = Artist.query.filter(Artist.name==request.form['name'])

  # on successful db insert, flash success
  except():
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  

  data=[]
  results = db.session.query(Show,Venue,Artist).select_from(Show).join(Venue).join(Artist).filter(Show.venue_id==Venue.id,Show.artist_id==Artist.id).all()
  for row in results:
    data.append({
      "venue_id":row.Show.venue_id,
      "venue_name":row.Venue.name,
      "artist_id":row.Show.artist_id,
      "artist_name":row.Artist.name,
      "artist_image_link":row.Artist.image_link,
      "start_time":row.Show.start_time
    })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form=ShowForm(request.form)
  try:
    if form.validate():

      show = Show(artist_id=request.form['artist_id'],venue_id=request.form['venue_id'],start_time=request.form['start_time'])
      form.populate_obj(show)
      db.session.add(show)
      db.session.commit()    
    
    
  # on successful db insert, flash success
      flash('Show was successfully listed!')
  except():
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')

  return render_template('pages/home.html')

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
