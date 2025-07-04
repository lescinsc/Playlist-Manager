import artistmethods
import auth
import time

sp = auth.create_connection()

def process_entries(entries):
    final_playlist_names = []
    final_playlist_ids = []
    # Filter out the 'done' used to redirect the form 
    entries = [entry for entry in entries if not (entry['artist'] == 'done' and entry['songs'] == 'done')]
    print(entries)
    for entry in entries:
        print(entry)
        artist = entry['artist']
        num_songs = entry['songs']
        time.sleep(0.2)  
        track_name, trac_id = artistmethods.get_random_tracks_from_artist(sp, artist, int(num_songs))
        final_playlist_names.extend(track_name)
        final_playlist_ids.extend(trac_id)
    return final_playlist_names, final_playlist_ids
       
