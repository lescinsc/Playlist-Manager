
import usermethods
import random


    
def get_random_tracks_from_artist(sp, artist_name, num_songs):
    results = sp.search(q=artist_name, type="artist", limit=12)
    print(f"Searching for artist: {artist_name}")
    if not results["artists"]["items"]:
        print(f"No artist found for '{artist_name}'")
        return [], []

    # Find the exact match
    artist_id = None
    for artist in results["artists"]["items"]:
        if artist["name"].lower() == artist_name.lower():
            artist_id = artist["id"]
            break

    if not artist_id:
        print(f"No exact match found for '{artist_name}'")
        return [], []

    # Get all albums & singles
    print(f"Found artist '{artist_name}' with ID: {artist_id}")
    albums = sp.artist_albums(artist_id, album_type='album,single')['items']
    album_tracks = []

    # Extract tracks from each album
    for album in albums:
        tracks = sp.album_tracks(album['id'])['items']
        album_tracks.extend([(track['name'], track['id'], artist_name) for track in tracks])

    # Get top tracks
    print(f"Fetching top tracks for artist '{artist_name}'")
    top_tracks = sp.artist_top_tracks(artist_id)["tracks"]
    top_track_data = [(track['name'], track['id'], artist_name) for track in top_tracks]

    # Ensure there's enough data to pull from
    if not album_tracks and not top_track_data:
        print(f"Insufficient track data for '{artist_name}'")
        return [], []

    # Shuffle both lists
    random.shuffle(album_tracks)
    random.shuffle(top_track_data)

    # Split selection
    half_num_songs = num_songs // 2
    selected_album_tracks = random.sample(album_tracks, min(half_num_songs, len(album_tracks)))
    selected_top_tracks = random.sample(top_track_data, min(num_songs - len(selected_album_tracks), len(top_track_data)))

    # Combine and separate into names and IDs
    combined_tracks = selected_album_tracks + selected_top_tracks

    return combined_tracks

def artist_exists(artist_name, sp):
    """
    Checks if an artist exists on Spotify.

    Parameters:
    - artist_name (str): The name of the artist to search for.
    - sp (spotipy.Spotify): An authenticated Spotipy client instance.

    Returns:
    - dict: Artist data if found, otherwise None.
    """
    results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
    artists = results.get('artists', {}).get('items', [])
    return 1 if artists else 0



