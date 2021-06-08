
from app import db

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

class Show(db.Model):
  __tablename__='Show'
  id=db.Column(db.Integer, primary_key=True)
  artist_id= db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'),nullable=False)
  start_time= db.Column(db.DateTime,nullable=False)

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