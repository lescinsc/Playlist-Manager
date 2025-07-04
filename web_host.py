from flask import Flask, render_template, request, redirect, url_for, session
from web_helpers import process_entries
from usermethods import get_or_create_playlist, add_track_to_playlist
import auth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def inputs():
    if 'entries' not in session:
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
            artist = request.form.get('artist_name')
            num_songs = request.form.get('num_songs')
            if artist and num_songs:
                session['entries'].append({'artist': artist, 'songs': num_songs})
                session.modified = True

    return render_template('inputs.html', entries=session['entries'])


@app.route('/done')
def done():
    entries = session.get('entries', [])

    finalplaylist = process_entries(entries)
    print(finalplaylist)
    track_names = finalplaylist[0]
    session['track_ids'] = finalplaylist[1]  # Store track IDs in session for later use
    session.pop('entries', None)
    return render_template('done.html', entries=track_names)



@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    playlist_name = request.form.get('playlist_name')

    sp = auth.create_connection()
    # Create the playlist
    uri = get_or_create_playlist(sp, playlist_name)
    for _track_id in session.get('track_ids', []):
        add_track_to_playlist(sp, uri, _track_id)
  

    # Clear session
    session.pop('track_ids', None)

    return f"<h2>Playlist '{playlist_name}' created!</h2><p><a href='{uri}' target='_blank'>Open Playlist</a></p>"

if __name__ == '__main__':
    app.run(debug=True)