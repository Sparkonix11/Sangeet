from flask import Blueprint, render_template, request, url_for, current_app, redirect, abort, jsonify
from flask_login import login_required, current_user
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from .models import Song, Album, SongRating, Playlist, Analytics, User
from . import db

UPLOAD_FOLDER = 'website/static/songs'
DB_UPLOAD_FOLDER = 'static/songs'
ALLOWED_EXTENSIONS = {'mp3'}


views = Blueprint('views', __name__)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def dashboard():
    user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()

    top_songs = db.session.query(Song, func.avg(Analytics.average_rating).label('avg_rating')) \
        .join(Analytics).group_by(Song.id).order_by(func.avg(Analytics.average_rating).desc()).limit(8).all()

    top_songs_with_ratings = []
    for song, avg_rating in top_songs:
        song_details = {
            'id': song.id,
            'title': song.title,
            'artist_id': song.artist_id,
            'artist': song.artist.name if song.artist else "Unknown",
            'average_rating': avg_rating,
            'image': song.image
        }
        top_songs_with_ratings.append(song_details)

    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_albums = Album.query.filter(Album.release_date >= thirty_days_ago) \
        .order_by(Album.release_date.desc()).limit(8).all()

    return render_template('dashboard.html', top_songs=top_songs_with_ratings, new_albums=new_albums, user_playlists = user_playlists)

@views.route('/admin/dashboard')
@login_required
def admin_dashboard():
    user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()

    top_songs = db.session.query(Song, func.avg(Analytics.average_rating).label('avg_rating')) \
        .join(Analytics).group_by(Song.id).order_by(func.avg(Analytics.average_rating).desc()).limit(8).all()

    top_songs_with_ratings = []
    for song, avg_rating in top_songs:
        song_details = {
            'id': song.id,
            'title': song.title,
            'artist_id': song.artist_id,
            'artist': song.artist.name if song.artist else "Unknown",
            'average_rating': avg_rating,
            'image': song.image
        }
        top_songs_with_ratings.append(song_details)

    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_albums = Album.query.filter(Album.release_date >= thirty_days_ago) \
        .order_by(Album.release_date.desc()).limit(8).all()
    total_users = User.query.count()
    total_creators = User.query.filter_by(role='creator').count()
    total_albums = Album.query.count()
    total_songs = Song.query.count()
    total_playlist = Playlist.query.count()
    all_users = User.query.all()
    all_creators = User.query.filter_by(role='creator').all()
    all_albums = Album.query.all()
    all_songs = Song.query.all()
    all_playlist = Playlist.query.all()
    all_ratings = {rating.song_id: rating.rating for rating in SongRating.query.all()}
    return render_template('admin_dashboard.html',user_ratings = all_ratings, top_songs=top_songs_with_ratings, new_albums=new_albums, user_playlists = user_playlists, total_albums = total_albums, total_creators = total_creators, total_users = total_users, total_songs = total_songs, total_playlist = total_playlist, all_albums = all_albums, all_creators = all_creators, all_playlist = all_playlist, all_songs = all_songs, all_users = all_users)

@views.route('/admin/user/toggle_flag_user/<int:user_id>', methods=['POST'])
@login_required
def toggle_flag_user(user_id):
    if current_user.role != 'admin':
        abort(403)  

    user = User.query.get_or_404(user_id)
    user.flagged = not user.flagged  
    db.session.commit()
    return redirect(url_for('views.admin_dashboard'))

@views.route('/admin/user/toggle_flag_album/<int:album_id>', methods=['POST'])
@login_required
def toggle_flag_album(album_id):
    if current_user.role != 'admin':
        abort(403)  

    album = Album.query.get_or_404(album_id)
    album.flagged = not album.flagged  
    db.session.commit()
    return redirect(url_for('views.admin_dashboard'))

@views.route('/admin/user/toggle_flag_song/<int:song_id>', methods=['POST'])
@login_required
def toggle_flag_song(song_id):
    if current_user.role != 'admin':
        abort(403)  

    song = Song.query.get_or_404(song_id)
    song.flagged = not song.flagged  
    db.session.commit()
    return redirect(url_for('views.admin_dashboard'))

# ------------------------------------------------------------------------------------------------------------------------

@views.route('/songs', methods=['GET'])
@login_required
def all_songs():
    user_id = current_user.id
    all_songs = Song.query.all()
    all_ratings = {rating.song_id: rating.rating for rating in SongRating.query.all()}

    return render_template('all_songs.html', songs=all_songs, user_ratings=all_ratings )

@views.route('/song/add', methods=['GET', 'POST'])
@login_required
def addsong():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)

        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename).replace('\\', '/')
            db_file_path = os.path.join(DB_UPLOAD_FOLDER, filename).replace('\\', '/')
            try:
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                file.save(file_path)

                image = request.files['image']
                db_image_path = '/static/song_placeholder.jpeg'
                if image.filename != '':
                    image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
                    db_image_path = os.path.join('/static', image.filename).replace('\\', '/')
                title = request.form['title']
                artist_id = current_user.id
                lyrics = request.form['lyrics']
                
                new_song = Song(title=title, artist_id=artist_id, file_path=db_file_path, lyrics = lyrics, image = db_image_path)

                db.session.add(new_song)
                db.session.commit()
                return redirect(url_for('views.user_songs'))

            except Exception as e:
                print(f"Error: {e}")
                db.session.rollback()

    return render_template("add_song.html")
@views.route('/song/<int:song_id>', methods=['GET'])
def play_song(song_id):
    song = Song.query.get(song_id)
    if song:
        return render_template('play_song.html', song=song)
    else:
        return render_template('song_not_found.html')
    
@views.route('/song/edit/<int:song_id>', methods=['GET', 'POST'])
@login_required
def edit_song(song_id):
    song = Song.query.get_or_404(song_id)

    if song.artist_id != current_user.id:
        abort(403)  

    if request.method == 'POST':
        form_title = request.form['title']
        form_lyrics = request.form['lyrics']

        image = request.files['image']
        if image.filename != '':
            image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
            db_image_path = os.path.join('/static', image.filename).replace('\\', '/')
            song.image = db_image_path
        song.title = form_title
        song.lyrics = form_lyrics
       

        try:
            db.session.commit()
            print('Song updated successfully', 'success')
            return redirect(url_for('views.user_songs'))
        except Exception as e:
            db.session.rollback()
            print('Failed to update song', 'error')

    return render_template('edit_song.html', song=song)

@views.route('/song/delete/<int:song_id>', methods=['GET', 'POST'])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)

    if song.artist_id != current_user.id:
        abort(403) 

    try:
        SongRating.query.filter_by(song_id=song_id).delete()
        Analytics.query.filter_by(song_id=song_id).delete()

        album_id = song.album_id  
        db.session.delete(song)
        db.session.commit()

        if album_id:
            album = Album.query.get(album_id)
            songs_in_album = Song.query.filter_by(album_id=album_id).count()

            if songs_in_album == 0:
                album.songs = [] 
            db.session.commit()
            print('Song deleted successfully', 'success')
        else:
            print('Song deleted successfully, no associated album', 'success')

    except Exception as e:
        db.session.rollback()
        print('Failed to delete song', e)

    return redirect(url_for('views.user_songs'))

@views.route('/user/songs', methods=['GET'])
@login_required
def user_songs():
    user_id = current_user.id
    user_songs = Song.query.filter_by(artist_id=user_id).all()
    user_ratings = {rating.song_id: rating.rating for rating in SongRating.query.filter_by(user_id=user_id).all()}

    return render_template('user_songs.html', songs=user_songs, user_ratings=user_ratings)



@views.route('/album/add', methods=['GET', 'POST'])
def add_album():
    if request.method == 'POST':
        title = request.form['title']
        release_date_str = request.form['release_date']
        image = request.files['image']
        db_image_path = '/static/album_placeholder.png'
        if image.filename != '':
            image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
            db_image_path = os.path.join('/static', image.filename).replace('\\', '/')
        selected_song_ids = request.form.getlist('songs')  

        release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()

        new_album = Album(title=title, release_date=release_date, artist_id=current_user.id, image = db_image_path)

        selected_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()
        new_album.songs.extend(selected_songs)

        try:
            db.session.add(new_album)
            db.session.commit()
            return redirect(url_for('views.user_albums'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return render_template('add_album.html', error="Failed to add the album")

    user_songs = Song.query.filter_by(artist_id=current_user.id).all()
    return render_template('add_album.html', user_songs=user_songs)

@views.route('/songs/rate/<int:song_id>/<int:rating>', methods=['POST'])
@login_required
def rate_song(song_id, rating):
    if rating < 1 or rating > 5:
        return jsonify({'message': 'Invalid rating'}), 400

    song = Song.query.get_or_404(song_id)

    existing_rating = SongRating.query.filter_by(song_id=song_id, user_id=current_user.id).first()

    if existing_rating:
        existing_rating.rating = rating
    else:
        new_rating = SongRating(song_id=song_id, user_id=current_user.id, rating=rating)
        db.session.add(new_rating)

    song_ratings = SongRating.query.filter_by(song_id=song_id).all()
    total_ratings = sum(r.rating for r in song_ratings)
    num_ratings = len(song_ratings)
    average_rating = total_ratings / num_ratings if num_ratings > 0 else 0

    song_analytics = Analytics.query.filter_by(song_id=song_id).first()
    if song_analytics:
        song_analytics.total_ratings = num_ratings
        song_analytics.average_rating = average_rating
        song_analytics.last_rating_date = datetime.now()
    else:
        new_analytics = Analytics(
            song_id=song_id,
            total_ratings=num_ratings,
            average_rating=average_rating,
            last_rating_date=datetime.now()
        )
        db.session.add(new_analytics)

    db.session.commit()

    return render_template('rate_confirmation.html', song_id=song_id, rating=rating)

# ------------------------------------------------------------------------------------------------------------

@views.route('/albums', methods=['GET'])
def all_albums():
    user_id = current_user.id
    user_albums = Album.query.all()

    return render_template('all_albums.html', user_albums=user_albums)


@views.route('/user/albums', methods=['GET'])
@login_required
def user_albums():
    user_id = current_user.id
    user_albums = Album.query.filter_by(artist_id=user_id).all()

    return render_template('user_albums.html', user_albums=user_albums)

@views.route('/album/<int:album_id>', methods=['GET'])
@login_required
def view_album(album_id):
    user_id = current_user.id
    album = Album.query.get_or_404(album_id)
    user_ratings = {rating.song_id: rating.rating for rating in SongRating.query.filter_by(user_id=user_id).all()}
    return render_template('view_album.html', album=album, user_ratings = user_ratings)

@views.route('/album/edit/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    album = Album.query.get_or_404(album_id)

    if album.artist_id != current_user.id:
        abort(403)  

    if request.method == 'POST':
        title = request.form['title']
        release_date_str = request.form['release_date']
        selected_song_ids = request.form.getlist('songs')  

        release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()

        album.title = title
        album.release_date = release_date

        image = request.files['image']
        if image.filename != '':
            image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
            db_image_path = os.path.join('/static', image.filename).replace('\\', '/')
            album.image = db_image_path

        selected_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()
        album.songs = selected_songs

        try:
            db.session.commit()
            return redirect(url_for('views.user_albums'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
    user_songs = Song.query.filter_by(artist_id=current_user.id).all()

    return render_template('edit_album.html', album=album, error="Failed to update the album", user_songs = user_songs)

@views.route('/album/delete/<int:album_id>', methods=['GET', 'POST'])
@login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)

    if album.artist_id != current_user.id:
        abort(403)  

    try:
        songs_in_album = Song.query.filter_by(album_id=album_id).all()
        for song in songs_in_album:
            song.album_id = None
        db.session.delete(album)
        db.session.commit()
        print('Album deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print('Failed to delete album', 'error')

    return redirect(url_for('views.user_albums'))

# ---------------------------------------------------------------------------------------------------

@views.route('/playlist/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if request.method == 'POST':
        playlist_name = request.form['playlist_name']
        selected_songs = request.form.getlist('selected_songs')
        image = request.files['image']
        db_image_path = '/static/playlist_placeholder.png'
        if image.filename != '':
            image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
            db_image_path = os.path.join('/static', image.filename).replace('\\', '/')

        new_playlist = Playlist(user_id=current_user.id, name=playlist_name, image = db_image_path)
        for song_id in selected_songs:
            song = Song.query.get(song_id)
            if song:
                new_playlist.songs.append(song)

        db.session.add(new_playlist)
        db.session.commit()
        print('Playlist created successfully', 'success')
        return redirect(url_for('views.user_playlists'))

    songs = Song.query.all()
    return render_template('create_playlist.html', songs=songs)

@views.route('/playlist/edit/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def edit_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    if playlist.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        playlist.name = request.form['playlist_name']
        image = request.files['image']
        if image.filename != '':
            image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
            db_image_path = os.path.join('/static', image.filename).replace('\\', '/')
            playlist.image = db_image_path

        selected_songs = request.form.getlist('selected_songs')

        playlist.songs = []

        for song_id in selected_songs:
            song = Song.query.get(song_id)
            if song:
                playlist.songs.append(song)

        db.session.commit()
        print('Playlist updated successfully', 'success')
        return redirect(url_for('views.user_playlists'))

    songs = Song.query.all()
    return render_template('edit_playlist.html', playlist=playlist, songs=songs)


@views.route('/playlist/delete/<int:playlist_id>', methods=['GET','POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    if playlist.user_id != current_user.id:
        abort(403) 

    try:
        db.session.delete(playlist)
        db.session.commit()
        print('Playlist deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print('Failed to delete playlist', 'error')

    return redirect(url_for('views.user_playlists'))

@views.route('/user/playlists', methods=['GET'])
@login_required
def user_playlists():
    user_id = current_user.id
    user_playlists = Playlist.query.filter_by(user_id=user_id).all()

    return render_template('user_playlists.html', user_playlists=user_playlists)


@views.route('/playlist/<int:playlist_id>', methods=['GET'])
@login_required
def view_playlist(playlist_id):
    user_id = current_user.id
    playlist = Playlist.query.get_or_404(playlist_id)
    user_ratings = {rating.song_id: rating.rating for rating in SongRating.query.filter_by(user_id=user_id).all()}
    return render_template('view_playlist.html', playlist=playlist, user_ratings = user_ratings)

# ------------------------------------------------------------------------------------------------------------------

@views.route('/search')
@login_required
def search_results():
    query = request.args.get('query')

    songs = Song.query.filter(or_(Song.title.ilike(f'%{query}%'), Song.lyrics.ilike(f'%{query}%'))).all()
    albums = Album.query.filter(Album.title.ilike(f'%{query}%')).all()
    playlists = Playlist.query.filter(Playlist.name.ilike(f'%{query}%')).all()
    analytics = Analytics.query.all()
    return render_template('search_results.html', songs=songs, albums=albums, playlists=playlists, analytics=analytics)

