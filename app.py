from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from web_helpers import process_entries
from usermethods import get_or_create_playlist, add_track_to_playlist
from artistmethods import artist_exists
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
load_dotenv()

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:5000/callback",
    scope="playlist-modify-public",
    show_dialog=True ,
    cache_path=".cache"
)

@app.route('/login', methods=['GET'])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'token_info' in session:
        sp = Spotify(auth=session['token_info']['access_token'])
        user_profile = sp.current_user()
        print(user_profile)

        if session.get('entries') is None:
            session['entries'] = []


        if request.method == 'POST':
            # Check if the 'done' button was pressed
            # Append a placeholder entry and redirect to the done page
            if 'done' in request.form:
                session['entries'].append({'artist': 'done', 'songs': 'done'})
                session.modified = True
                return redirect(url_for('done'))
            # Otherwise, keep getting input from the user
            else:
                print(session['entries'])
                artist = request.form.get('artist_name')
                num_songs = request.form.get('num_songs')
                if artist and num_songs:
                    if artist_exists(artist, sp):
                        session['entries'].append({'artist': artist, 'songs': num_songs})
                        session.modified = True
                    else:
                        return render_template('inputs.html', entries=session['entries'], user=user_profile['display_name'], message=f"Artist '{artist}' not found on Spotify.")

    
        return render_template('inputs.html', entries=session['entries'], user=user_profile['display_name'])
    else:
        return '<a href="/login">Log in with Spotify</a>'





@app.route('/done')
def done():
    entries = session.get('entries', [])
    sp = Spotify(auth=session['token_info']['access_token'])
    finalplaylist = process_entries(sp, entries)
    print(finalplaylist)
    track_names = finalplaylist[0]
    session['track_ids'] = finalplaylist[1]  # Store track IDs in session for later use
    session.pop('entries', None)
    return render_template('done.html', entries=track_names)



@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    sp = Spotify(auth=session['token_info']['access_token'])
    playlist_name = request.form.get('playlist_name')

    # Create the playlist
    uri = get_or_create_playlist(sp, playlist_name)
    for _track_id in session.get('track_ids', []):
        add_track_to_playlist(sp, uri, _track_id)
  

    # Clear session
    session.pop('track_ids', None)

    return f"<h2>Playlist '{playlist_name}' created!</h2><p><a href='{uri}' target='_blank'>Open Playlist</a></p>"

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