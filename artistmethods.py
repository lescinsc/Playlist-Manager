import auth
import usermethods
import random


sp = auth.create_connection()

    
def get_random_songs_from_this_is(sp, artist_name, num_songs):
    query = f"{artist_name}"

    results = sp.search(q=query, type="playlist", limit=10)
    if results["playlists"]["items"]:
        playlist_id = results["playlists"]["items"][0]["id"]
        tracks = sp.playlist_tracks(playlist_id)["items"]
        
        if tracks:
            random_tracks = random.sample(tracks, min(num_songs, len(tracks)))
            return [track["track"]["uri"] for track in random_tracks]
        else:
            print("No tracks found in the playlist.")
            return []
    else:
        print(f"No playlist found for 'This Is {artist_name}'")
        return []

def get_random_tracks_from_artist(sp, artist_name, num_songs):
    results = sp.search(q=artist_name, type="artist", limit=12)
    if not results["artists"]["items"]:
        print(f"No artist found for '{artist_name}'")
        return []

    # Find the exact match
    artist_id = None
    for artist in results["artists"]["items"]:
        if artist["name"].lower() == artist_name.lower():
            artist_id = artist["id"]
            break

    if not artist_id:
        print(f"No exact match found for '{artist_name}'")
        return []


    # Get all albums & singles
    albums = sp.artist_albums(artist_id, album_type='album,single')['items']
    track_list = []

    # Extract tracks from each album
    for album in albums:
        album_tracks = sp.album_tracks(album['id'])['items']
        track_list.extend([track['id'] for track in album_tracks])

    # Get top tracks
    top_tracks = sp.artist_top_tracks(artist_id)["tracks"]
    top_track_list = [track['id'] for track in top_tracks]

    # Ensure there's enough data to pull from
    if not track_list or not top_track_list:
        print(f"Insufficient track data for '{artist_name}'")
        return []

    # Shuffle both lists
    random.shuffle(track_list)
    random.shuffle(top_track_list)

    # Split selection
    half_num_songs = num_songs // 2
    random_album_tracks = random.sample(track_list, min(half_num_songs, len(track_list)))
    random_top_tracks = random.sample(top_track_list, min(num_songs - len(random_album_tracks), len(top_track_list)))

    return random_album_tracks + random_top_tracks
