




def add_track_to_playlist(sp, playlist_id, track_uri):
    sp.playlist_add_items(playlist_id, [track_uri])

def get_user_playlists(sp):
    user_id = sp.me()["id"]  # Get the user's Spotify ID
    return  sp.user_playlists(user_id)["items"] 

def get_user_playlist_names(sp):
    playlists = get_user_playlists(sp)
    # filter out only names
    return [playlist["name"] for playlist in playlists]

def create_playlist(sp, playlist_name):
 
    playlists = get_user_playlists(sp)  # Get user's playlists
    
    # Check if playlist already exists
    for playlist in playlists:
        if playlist["name"].lower() == playlist_name.lower():
            print(f"Playlist '{playlist_name}' already exists. Returning URI.")
            sp.playlist_replace_items(playlist["uri"], [])  # Wipe the playlist
            return playlist["uri"]
    
    # Create a new playlist if it doesn't exist
    new_playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=True)
    print(f"Created new playlist '{playlist_name}'. Returning URI.")
    return new_playlist["uri"]


