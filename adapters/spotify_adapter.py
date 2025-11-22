import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def buscar_en_spotify(query):
    """
    Busca una canción en Spotify y devuelve su URL.
    """
    results = sp.search(q=query, limit=1, type='track')
    items = results['tracks']['items']
    if len(items) > 0:
        track = items[0]
        return {'nombre': track['name'], 'url': track['external_urls']['spotify']}
    else:
        return None

def crear_playlist(nombre, canciones):
    """
    Crea una playlist con el nombre dado y añade las canciones (URIs o URLs).
    """
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user=user_id, name=nombre, public=True)
    if canciones:
        sp.playlist_add_items(playlist_id=playlist['id'], items=canciones)
    return playlist['external_urls']['spotify']
