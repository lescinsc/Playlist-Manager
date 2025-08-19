import artistmethods
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
