import artistmethods
from flask import redirect, url_for, session
from spotipy import Spotify
import auth
import time


def process_entries(sp, entries):
    final_playlist = []
    # Filter out the 'done' used to redirect the form 
    entries = [entry for entry in entries if not (entry['artist'] == 'done' and entry['songs'] == 'done')]
    print(entries)
    for entry in entries:
        print(entry)
        artist = entry['artist']
        num_songs = entry['songs']
        time.sleep(0.1)  
        combined_tracks = artistmethods.get_random_tracks_from_artist(sp, artist, int(num_songs))
        final_playlist.extend(combined_tracks)
    return final_playlist

def check_artist_added(artist, user_input):
    for entry in user_input:
        if entry.get('artist') == artist:
            return True
    return False

def remove_done(user_input):
    filtered_user_input = []
    for entry in user_input:
        print("Entry: ", entry)
        if (entry.get('artist') != 'done' and entry.get('songs') != 'done'):
            filtered_user_input.append(entry)
    return filtered_user_input
    
def check_profile(session):
    try:
        # Try to get the user profile with the token info 
        sp = Spotify(auth=session['token_info']['access_token'])
        
        return True
        # If it fails, redirect to login
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return False