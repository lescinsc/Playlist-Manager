import auth 

sp = auth.create_connection()


def add_track_to_playlist(sp, playlist_id, track_uri):
    sp.playlist_add_items(playlist_id, [track_uri])

def get_or_create_playlist(sp, playlist_name):
    user_id = sp.me()["id"]  # Get the user's Spotify ID
    playlists = sp.user_playlists(user_id)["items"]  # Get user's playlists
    
    # Check if playlist already exists
    for playlist in playlists:
        if playlist["name"].lower() == playlist_name.lower():
            print(f"Playlist '{playlist_name}' already exists. Returning URI.")
            return playlist["uri"]
    
    # Create a new playlist if it doesn't exist
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    print(f"Created new playlist '{playlist_name}'. Returning URI.")
    return new_playlist["uri"]


