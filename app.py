from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from web_helpers import check_profile ,process_entries, check_artist_added, remove_done
from usermethods import get_user_playlists, get_user_playlist_names, create_playlist, add_track_to_playlist
from artistmethods import artist_exists, get_random_tracks_from_artist
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_PERMANENT'] = False

# Load environment variables from .env file
load_dotenv()


sp_oauth = SpotifyOAuth(
    # Set in env file
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    #redirect_uri="https://playlist-manager-n6nm.onrender.com/callback",
    redirect_uri="http://127.0.0.1:5000/callback",
    requests_timeout=10,  # Increase timeout here
    scope="playlist-modify-public",
    show_dialog=True ,
    cache_path=".cache"
)

@app.route('/')
def home():
    return render_template('home.html')

# Displays url to login with Spotify
@app.route('/login', methods=['GET'])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Call back from spotify
# Append token info to session 
# Redeirect to playlist_creator
@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('playlist_view'))

@app.route('/playlist_view', methods=['GET'])
def playlist_view():
    if  check_profile(session):
        return render_template('playlist_view.html', playlists=get_user_playlist_names(Spotify(auth=session['token_info']['access_token'])))
    else:
        return redirect(url_for('login'))


@app.route('/playlist_creator', methods=['GET', 'POST'])
def playlist_creator():
    sp = Spotify(auth=session['token_info']['access_token'])
    user_profile = sp.current_user()
        # Init entries list
    if session.get('user_input') is None:
        session['user_input'] = []
        # Check if the 'done' button was pressed
        # Append a placeholder entry and redirect to the done page
    if 'done' in request.form:
        session['user_input'].append({'artist': 'done', 'songs': 'done'})
        session.modified = True
        return redirect(url_for('playlist'))
    # Otherwise, keep getting input from the user
    else:
        artist = request.form.get('artist_name')
        num_songs = request.form.get('num_songs')
        if check_artist_added(artist, session['user_input']):
            # If artist already added, show an error message
            return render_template('inputs.html', entries=session['user_input'], user=user_profile['display_name'], message=f"Artist '{artist}' already added.")
        if artist and num_songs:
            if artist_exists(artist, sp):
                session['user_input'].append({'artist': artist, 'songs': num_songs})
                session.modified = True
            else:
                # If artist does not exist, show an error message
                return render_template('inputs.html', entries=session['user_input'], user=user_profile['display_name'], message=f"Artist '{artist}' not found on Spotify.")
    return render_template('inputs.html', entries=session['user_input'], user=user_profile['display_name'])





@app.route('/playlist', methods=['GET', "GET"])
def playlist():
    sp = Spotify(auth=session['token_info']['access_token'])
    finalplaylist = process_entries(sp, session.get('user_input', []))
    print(finalplaylist)
    # Store artists for display
    session['playlist'] = finalplaylist
    return render_template('playlist.html', playlist=finalplaylist)





@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    session.pop('user_input', None)
    sp = Spotify(auth=session['token_info']['access_token'])
    playlist_name = request.form.get('playlist_name')

    # Create the playlist
    playlist_uri = create_playlist(sp, playlist_name)
    for song in session.get(session['playlist'], []):
        print(("Adding track:", song))
        add_track_to_playlist(sp, playlist_uri, song[2])
    # Clear session
    session.pop('playlist', None)

    return f"<h2>Playlist '{playlist_name}' created!</h2><p><a href='{playlist_uri}' target='_blank'>Open Playlist</a></p>"

@app.route('/remove/<artist_name>', methods=['GET'])
def remove_artist(artist_name):
    filtered_user_input = []
    for entry in session.get('user_input', []):
        if entry.get('artist') != artist_name:
            filtered_user_input.append(entry)
    session['user_input'] = filtered_user_input
    return redirect(url_for('playlist_creator'))

@app.route('/replace_song', methods=['GET'])
def replace_song():
    track_name = request.args.get('track_name')
    artist = request.args.get('artist_name')
    filtered_entries = []
    for entr in session['playlist']:
        print("Entris: ", entr)
        if entr[2] != artist or entr[0] != track_name:
            filtered_entries.append(entr)
    sp = Spotify(auth=session['token_info']['access_token'])
    num_songs = 1  
    trakc_info = get_random_tracks_from_artist(sp, artist, num_songs)
    if trakc_info:
        filtered_entries.append((trakc_info[0][0], trakc_info[0][1], trakc_info[0][2]))
    session['playlist'] = filtered_entries
    return render_template('playlist.html', playlist=filtered_entries)

@app.route('/redirect_from_playlist', methods=['GET'])
def redirect_from_playlist():
    session['user_input'] = remove_done(session.get('user_input', []))
    return redirect(url_for('playlist_creator'))

@app.route('/logout')
def logout():
    if os.path.exists(".cache"):
        os.remove(".cache")


    # Clear session data
    session.clear()

    # Redirect to playlist_creator or login page
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)