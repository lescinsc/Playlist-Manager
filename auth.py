import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Set up authentication





def create_connection():
    client_id="df2c47e8ba6345c18b2139b578149d07"
    client_secret="2eafc48ba07348b8b76d19689b2c815e"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret= client_secret,
        redirect_uri="http://127.0.0.1:5000/",
        scope="user-library-read playlist-modify-private playlist-read-collaborative playlist-modify-private playlist-modify-public"
    ))
    return sp


