import requests
import json
API_url = "https://api.spotify.com/v1/"


SPOTIFY_ACCESS_TOKEN = "BQAgjcrfczi6FnZx5Qrnef49oIr7N0twGQZ14r98ZPCZQpPWmYCKfSQGVr-ll_Mhku7E4jkwrPx_ZIgqIEXTgXnHV_q4yE0LO7K2VHg1gvxR3HzdUcpfYAmKumRVSoe-iB4GqAT_bkA"
SEARCH_URL = "https://api.spotify.com/v1/search"

def buscar_en_spotify(query, tipo="track", limite=2):
    """
    Busca música en la API de Spotify usando un token de acceso.

    Args:
        query (str): El término de búsqueda (ej: "Bohemian Rhapsody").
        tipo (str): El tipo de elemento a buscar (ej: "track", "artist", "album").
        limite (int): El número máximo de resultados a devolver.

    Returns:
        dict or str: Los datos JSON de la respuesta o un mensaje de error.
    """
    headers = {
        "Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"
    }
    parametros = {
        "q": query,
        "type": tipo,
        "limit": limite
    }

    try:
        respuesta = requests.get(SEARCH_URL, headers=headers, params=parametros)
        respuesta.raise_for_status()  # Lanza una excepción para errores HTTP (4xx o 5xx)
        resultados = respuesta.json()["tracks"]["items"]
        lista = []
        for resultado in resultados:
            lista.append({"nombre":resultado["name"], "URL":resultado["external_urls"]["spotify"]})

        return lista
    
    except requests.exceptions.RequestException as e:
        return f"Error al realizar la solicitud a Spotify: {e}"

respuesta = buscar_en_spotify(query="tu misterioso alguien")
print(respuesta)