from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from web_helpers import process_entries
from usermethods import get_or_create_playlist, add_track_to_playlist
from artistmethods import artist_exists
from artistmethods import get_random_tracks_from_artist
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
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

# Displays url to login with Spotify
@app.route('/login', methods=['GET'])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Call back from spotify
# Append token info to session 
# Redeirect to home
@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    # If logged in 
    if 'token_info' in session:
        try:
            # Try to get the user profile with the token info 
            sp = Spotify(auth=session['token_info']['access_token'])
            user_profile = sp.current_user()
            # If it fails, redirect to login
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return redirect(url_for('login'))
        # Init entries list
        if session.get('user_input') is None:
            session['user_input'] = []
        if request.method == 'POST':
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
                if artist and num_songs:
                    if artist_exists(artist, sp):
                        session['user_input'].append({'artist': artist, 'songs': num_songs})
                        session.modified = True
                    else:
                        # If artist does not exist, show an error message
                        return render_template('inputs.html', entries=session['user_input'], user=user_profile['display_name'], message=f"Artist '{artist}' not found on Spotify.")
        return render_template('inputs.html', entries=session['user_input'], user=user_profile['display_name'])
    else:
        # If not logged in, show the login link
        return '<a href="/login">Log in with Spotify</a>'





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
    playlist_uri = get_or_create_playlist(sp, playlist_name)
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
    return redirect(url_for('home'))

@app.route('/replace_song', methods=['Post'])
def replace_song():
    track_name = request.args.get('track_name')
    artist = request.args.get('artist_name')
    filtered_entries = []
    print("Current Playlist: ", session['playlist'])
    print("Replace Song: ", track_name)
    print("Replace Artist: ", artist)
    for entr in session['playlist']:
        print("Entris: ", entr)
        if entr[2] != artist or entr[0] != track_name:
            filtered_entries.append(entr)
    sp = Spotify(auth=session['token_info']['access_token'])
    num_songs = 1  
    trakc_info = get_random_tracks_from_artist(sp, artist, num_songs)
    print("Track Info: ", trakc_info)
    if trakc_info:
        filtered_entries.append((trakc_info[0][0], trakc_info[0][1], trakc_info[0][2]))
    session['playlist'] = filtered_entries
    print("TEST: ")
    return render_template('playlist.html', playlist=filtered_entries)



@app.route('/logout')
def logout():
    if os.path.exists(".cache"):
        os.remove(".cache")


    # Clear session data
    session.clear()

    # Redirect to home or login page
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)