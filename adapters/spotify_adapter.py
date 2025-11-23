import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def buscar_en_spotify(query, search_type="track"):
    if search_type == 'podcast':
        api_type = 'show'
    elif search_type == 'track':   
        api_type = 'track'
    else:  
        api_type = search_type
    results = sp.search(q=query, limit=1, type=api_type)
    key_plural = api_type + 's'
    if api_type == 'show':
        key_plural = 'shows'   
    items = results.get(key_plural, {}).get('items', [])
    if len(items) > 0:
        item = items[0]   
        return {'nombre': item.get('name', 'N/A'), 'url': item['external_urls']['spotify']}
    else:
        return {'nombre': 'No encontrado', 'url': None} 

def crear_playlist(nombre, canciones):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user=user_id, name=nombre, public=True)
    if canciones:
        sp.playlist_add_items(playlist_id=playlist['id'], items=canciones)
    return playlist['external_urls']['spotify']