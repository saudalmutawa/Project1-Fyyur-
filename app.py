#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
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
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

TEMPLATES_AUTO_RELOAD = True

# TODO: connect to a local postgresql database(SOLVED)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
current_time=time.strftime('%Y-%m-%d %H:%S:%M',time.localtime(time.time()))
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False,unique=True)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120),nullable=False)
    genres=db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String())
    venue_shows=db.relationship('Show',backref=db.backref('venues',lazy=True), cascade='all,delete')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate(SOLVED)
# Show = db.Table('Show',
# db.Column('id', db.Integer, primary_key=True),
# db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'),nullable=False),
# db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'),nullable=False),
# db.Column('start_time', db.DateTime,nullable=False,default=current_time)
class Show(db.Model):
  __tablename__='Show'
  id=db.Column(db.Integer, primary_key=True)
  artist_id= db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'),nullable=False)
  start_time= db.Column(db.DateTime,nullable=False,default=current_time)

# venue=db.relationship('Venue',backref='Show'),
# artist=db.relationship('Artist',backref='Show'),


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String())
    artist_shows=db.relationship('Show',backref=db.backref('artists',lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate(SOLVED) 
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.(SOLVED)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. (SOLVED)
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
  # data=[{

  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(SOLVED)
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  resultt = request.form.get('search_term', '') #store search result
  print(resultt)
  query=Venue.query.filter(Venue.name.ilike('%'+resultt+'%')).all()  #search in database where there is a partial string from the result
  venuesdata=[]
  for row in query: #loop through venue objects 
    upcomingshows=db.session.query(Show,Venue).select_from(Venue).join(Show).filter(and_(Show.venue_id==row.id,Show.c.start_time>current_time)).all()
    count=len(upcomingshows)
    venuesdata.append({
      "id":row.id,
      "name":row.name,
      "num_upcoming_shows":count
    })
  response={
    "count":len(query),
    "data":venuesdata  
   
   
   
    # "data": [{
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "num_upcoming_shows": 0,
    # }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id (SOLVED)
  query1 = Venue.query.get(venue_id)
  genrelist=query1.genres.split(",")
  upcomingshows=db.session.query(Show,Venue).select_from(Venue).join(Show).filter(and_(Show.venue_id==query1.id, Show.start_time>current_time)).all()
  countup=len(upcomingshows)
 # pastshows=Venue.query.join(Show).filter(Show.c.venue_id==venue_id , Show.c.start_time<=current_time ).all()
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
   # TODO: insert form data as a new Venue record in the db, instead(SOLVED)
  # TODO: modify data to be the data object returned from db insertion (SOLVED)
  seeking=False
  if request.form.get("seeking_talent",False)=="y":
      seeking=True
  else:
    seeking=False

  try:
    venue_data=Venue(name=request.form['name'],city=request.form['city'],state=request.form['state'],address=request.form['address'],phone = request.form['phone'],genres=request.form['genres'],facebook_link=request.form['facebook_link'],image_link=request.form['image_link'],website=request.form['website_link'],seeking_talent=seeking,seeking_description=request.form['seeking_description'])
    db.session.add(venue_data)
    db.session.commit()
    data = Venue.query.filter(Venue.name==request.form['name'])
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except():
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete_venue', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.(SOLVED)
  error=False
  try:
    venue1=Venue.query.get(venue_id)
    db.session.delete(venue1)
    db.session.commit()
  except():
    db.session.rollback()
    error=True
  
  if error:
    abort(500)
  else:
    return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage(SOLVED)
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database(SOLVED)
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
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(SOLVED)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  result=request.form.get('search_term', '')
  rows = Artist.query.filter(Artist.name.ilike('%'+result+'%')).all()
  data=[]
  for row in rows:
    upcomingshows=db.session.query(Show,Artist).select_from(Artist).join(Show).filter(Show.venue_id==Artist.id,Show.start_time>current_time).all()
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
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id(SOLVED)
  
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

  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
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
  # TODO: populate form with fields from artist with ID <artist_id>(SOLVED)
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
  # TODO: take values from the form submitted, and update existing(SOLVED)
  # artist record with ID <artist_id> using the new attributes


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
  # TODO: populate form with values from venue with ID <venue_id>(SOLVED)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing(SOLVED)
  # venue record with ID <venue_id> using the new attributes(SOLVED)
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead(SOLVED)
  # TODO: modify data to be the data object returned from db insertion(SOLVED)
  seeking=False
  if request.form.get("seeking_venue",False)=="y":
      seeking=True
  else:
   seeking=False

  try:
    artist_data=Artist(name=request.form['name'],city=request.form['city'],state=request.form['state'],phone = request.form['phone'],genres=request.form['genres'],facebook_link=request.form['facebook_link'],image_link=request.form['image_link'],website=request.form['website_link'],seeking_venue=seeking,seeking_description=request.form['seeking_description'])
    db.session.add(artist_data)
    db.session.commit()
    data = Artist.query.filter(Artist.name==request.form['name'])

  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except():
    # TODO: on unsuccessful db insert, flash an error instead.(SOLVED)
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

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
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead(SOLVED)
  try:
    # ven=Venue.query.filter(Venue.id==request.form['venue_id']).first()
    # art=Artist.query.filter(Artist.id==request.form['artist_id']).first()
    # art.venues.append(ven)
    # sho=Show(artist_id=request.form['artist_id'],venue_id=request.form['venue_id'],start_time=request.form['start_time'])
    show = Show(artist_id=request.form['artist_id'],venue_id=request.form['venue_id'],start_time=request.form['start_time'])
    db.session.add(show)
    db.session.commit()    
    
    
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except():
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.(SOLVED)
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
