from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    image = db.Column(db.String(200), nullable=False, default = '/static/user_placeholder.png')
    flagged = db.Column(db.Boolean, default=False)
    songs = db.relationship('Song', backref='artist', lazy=True)
    albums = db.relationship('Album', backref='artist', lazy=True)
    song_ratings = db.relationship('SongRating', backref='user', lazy=True)
    

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lyrics = db.Column(db.Text)
    file_path = db.Column(db.String(200), nullable=False) 
    image = db.Column(db.String(200), nullable=False, default = '/static/song_placeholder.jpeg')
    flagged = db.Column(db.Boolean, default=False)
    ratings = db.relationship('SongRating', backref='song', lazy=True)
    analytics = db.relationship('Analytics', backref='song', lazy=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    release_date = db.Column(db.Date)
    flagged = db.Column(db.Boolean, default=False)
    image = db.Column(db.String(200), nullable=False, default = '/static/album_placeholder.jpeg')  
    songs = db.relationship('Song', backref='album', lazy=True)

class SongRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    total_ratings = db.Column(db.Integer, nullable=False)
    average_rating = db.Column(db.Float, nullable=False)
    last_rating_date = db.Column(db.DateTime, nullable=False)


class AdminAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_users = db.Column(db.Integer, nullable=False)
    total_songs = db.Column(db.Integer, nullable=False)
    total_albums = db.Column(db.Integer, nullable=False)
    total_ratings = db.Column(db.Integer, nullable=False)
    average_song_ratings = db.Column(db.Float, nullable=False)
    most_rated_song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    least_rated_song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    
    most_rated_song = db.relationship('Song', foreign_keys=[most_rated_song_id])
    least_rated_song = db.relationship('Song', foreign_keys=[least_rated_song_id])


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False, default = '/static/playlist_placeholder.jpeg')
    songs = db.relationship('Song', secondary='playlist_songs', backref='playlists', lazy='dynamic')

playlist_songs = db.Table('playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)
