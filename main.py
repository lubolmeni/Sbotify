import telebot
from adapters.gemini_adapter import preguntar_gemini
import os
from dotenv import load_dotenv
import typing_extensions as typing
from adapters.spotify_adapter import crear_playlist, buscar_en_spotify
import json
load_dotenv()

# --- VARIABLE DE VERSIÓN ---
BOT_VERSION = "1.0.0-alpha"

# --- DEFINICIONES DE TIPOS GLOBALES ---
# Usado por /animo, /recomendar, y /situación
class RespuestaSpotify(typing.TypedDict):
    keywords: str
    search_type: typing.Literal["track", "playlist", "album", "artist", "podcast"]

# Usado por /playlist
class RespuestaPlaylist(typing.TypedDict):
    nombre: str
    canciones: list[str]
# --------------------------------------

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

# --- HANDLER: Comando /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bienvenida = (
        "👋 **Bienvenidos a Sbotify**, su asistente personal para elegir la música que necesitan en el momento que necesitan.\n\n"
        "Tenés las siguientes opciones para elegir tu próxima canción o playlist para disfrutar:\n\n"
        "🎶 **/animo [estado]**: Pedí una canción o playlist en relación a como te sientas en este momento.\n"
        "🗺️ **/situación [descripción]**: Pedile al bot una playlist para un momento determinado de tu día (estudiar, cocinar, etc.).\n"
        "🎧 **/recomendar [tema/artista]**: Descubrí la mejor música de una época o lugar determinado (ej: artistas similares a The Cure).\n"
        "➕ **/playlist [canciones]**: Creá una playlist con una lista de canciones específicas.\n\n"
        "Todas estas opciones van a ser redirigidas a tu Spotify para que puedas seguirlo escuchando cuando quieras. Dicho todo esto... ¿Qué tenés ganas de escuchar hoy?"
        "\n\n/animo\n/situación\n/recomendar"
    )
    bot.reply_to(message, bienvenida, parse_mode='Markdown')

# --- HANDLER: Comando /version ---
@bot.message_handler(commands=['version'])
def send_version(message):
    """Responde con la versión actual del bot."""
    respuesta = f"🤖 La versión actual de Sbotify es: **{BOT_VERSION}**"
    bot.reply_to(message, respuesta, parse_mode='Markdown')

# --- HANDLER MODIFICADO: Comando /situación (Mismo estilo de recomendación que /animo y /recomendar) ---
@bot.message_handler(commands=['situación', 'situacion'])
def send_situacion_recommendation(message):
    
    # Extraer la situación del usuario y limpiar ambos comandos
    user_situation = message.text.replace("/situacion", "", 1).replace("/situación", "", 1).strip()

    # --- LÓGICA DE AUTOCOMPLETADO (Prompt para el usuario) ---
    if not user_situation:
        bot.reply_to(message, "💬 Por favor, describí la situación para la que querés la recomendación. Ejemplo: `/situacion necesito música instrumental tranquila para estudiar concentrado`")
        return

    try:
        # --- 1. Petición a Gemini para generar las búsquedas y el tipo de contenido ---
        instrucciones_keywords = (
            "Vas a recibir la descripción de una situación específica (ej: estudiar, cocinar, viajar, etc.). "
            "Tu tarea es generar las palabras clave ('keywords') MÁS ESPECÍFICAS posibles para buscar en Spotify un contenido que se adapte perfectamente al ambiente y ritmo de esa situación. "
            "Céntrate en géneros, estilo y tempo. Elige el 'search_type' más relevante de la lista: 'track', 'playlist', o 'album'. Una 'playlist' o 'album' suelen ser mejores para actividades largas."
        )
        
        resultado_keywords_json = preguntar_gemini(
            pregunta=f"Situación del usuario: {user_situation}",
            instrucciones=instrucciones_keywords,
            estructura_salida=RespuestaSpotify
        )

        resultado_keywords = json.loads(resultado_keywords_json)
        keywords = resultado_keywords["keywords"]
        search_type = resultado_keywords["search_type"]

        # --- 2. Buscar en Spotify la recomendación (Una sola búsqueda) ---
        spotify_result = buscar_en_spotify(keywords, search_type=search_type)
        recomendacion_url = spotify_result.get("url")

        if not recomendacion_url:
             bot.reply_to(message, f"❌ Lo siento, no encontré un resultado relevante en Spotify para la situación: '{user_situation}' con la búsqueda '{keywords}'.")
             return

        # --- 3. Generar la respuesta final con Gemini ---
        instrucciones_respuesta_final = (
            "Vas a recibir la situación original de un usuario y el enlace de Spotify que se acaba de encontrar."
            "\n\n**TU TAREA PRINCIPAL ES GENERAR EL MENSAJE FINAL COMPLETO:**"
            "\n1. **Estilo:** La respuesta debe usar el **voseo** y tener un tono **amigable, informal y entusiasta**. Agregá emojis para hacerlo más canchero."
            "\n2. **Contenido:** Generá un mensaje de **dos a tres líneas** que confirme la recomendación, mencione el tipo de contenido (playlist, álbum, etc.) y que invite al usuario a disfrutar de la música para su situación."
            "\n3. **Formato Final:** La respuesta debe ser UN ÚNICO BLOQUE DE TEXTO que combine el comentario y contenga el URL de Spotify en una línea separada."
        )

        respuesta = preguntar_gemini(
            pregunta=f"Situación original: {user_situation} \n Tipo de contenido sugerido: {search_type} \n URL de Spotify: {recomendacion_url}",
            instrucciones=instrucciones_respuesta_final
        )
        
        bot.reply_to(message, respuesta)
    
    except json.JSONDecodeError:
        bot.reply_to(message, "Hubo un error al procesar la respuesta de Gemini (formato JSON inválido).")
    except Exception as e:
        print("\n" + "="*50)
        print(f"!!! ERROR GENERAL CAPTURADO !!!")
        print(f"Tipo de Error: {type(e).__name__}")
        print(f"Mensaje de Error: {e}")
        print("="*50 + "\n")
        bot.reply_to(message, "❌ Lo siento, hubo un error general al intentar obtener la recomendación para tu situación. Revisá la consola para más detalles.")

    print("Mensaje de recomendación por situación enviado.")

@bot.message_handler(commands=['animo'])
def send_welcome(message):

    user_mood = message.text.replace("/animo", "", 1).strip()

    # --- LÓGICA DE AUTOCOMPLETADO (Prompt para el usuario) ---
    if not user_mood:
        bot.reply_to(message, "💬 Por favor, decime cómo te sentís. Ejemplo: `/animo necesito algo tranquilo porque estoy triste`")
        return

    try:
        instrucciones_keywords = (
            "Vas a recibir el estado de ánimo o una descripción de cómo se siente una persona. Tu tarea es generar las palabras clave ('keywords') MÁS ESPECÍFICAS posibles para buscar **UNA CANCIÓN (track)** en Spotify que ayude a la persona a sentirse mejor o a encontrar el consuelo que busca o lo que tu recominedes segun su estado de animo. "
            "Céntrate en géneros, estilo y sentimientos (Ej: 'soul', 'música instrumental para ansiedad', 'pop optimista de los 80'). "
            "Elige 'track' como 'search_type'."
        )

        resultado_keywords_json = preguntar_gemini(
            pregunta=f"Estado de ánimo del usuario: {user_mood}",
            instrucciones=instrucciones_keywords,
            estructura_salida=RespuestaSpotify
        )

        resultado_keywords = json.loads(resultado_keywords_json)
        keywords = resultado_keywords["keywords"]
        search_type = resultado_keywords["search_type"]

        spotify_result = buscar_en_spotify(keywords, search_type=search_type)
        recomendacion_url = spotify_result.get("url")

        if not recomendacion_url:
             bot.reply_to(message, f"Lo siento, no encontré un resultado relevante en Spotify para la búsqueda '{keywords}'.")
             return

        instrucciones_respuesta_final = (
            "Vas a recibir el estado de ánimo de un usuario y el enlace de una canción de Spotify."
            "\n\n**TU TAREA PRINCIPAL ES GENERAR EL MENSAJE FINAL COMPLETO:**"
            "\n1. **Estilo:** La respuesta debe usar el **voseo** y tener un tono **amigable, informal, pero no tanto y natural. Puedes agregar emojis para hacerlo más sentido.**."
            "\n2. **Contenido:** Debes generar un mensaje de **dos a tres líneas** que introduzca la canción y luego, **al final**, debes incluir una frase o palabra de **ánimo, motivación o buena onda** que sea relevante al estado de ánimo que describió el usuario."
            "\n3. **Separación:** Luego de la introducción, DEJA UN ESPACIO DE LÍNEA EN BLANCO antes de colocar el enlace. Después del enlace, DEJA OTRO ESPACIO DE LÍNEA EN BLANCO antes de dar el mensaje de ánimo."
            "\n4. **Formato Final:** La respuesta debe ser UN ÚNICO BLOQUE DE TEXTO que combine el comentario y contenga: [Introducción]\n\n[Enlace Spotify]\n\n[Frase de Ánimo]."
        )

        respuesta = preguntar_gemini(
            pregunta=f"Estado de ánimo del usuario: {user_mood} \n Enlace de la canción: {recomendacion_url}",
            instrucciones=instrucciones_respuesta_final
        )

        bot.reply_to(message, respuesta)

    except json.JSONDecodeError:
        bot.reply_to(message, "Hubo un error al procesar la respuesta de Gemini (formato JSON inválido).")
    except KeyError as e:
        bot.reply_to(message, f"Error: Faltó una clave esperada en el resultado. Clave faltante: {e}.")
    except Exception as e:
        print("\n" + "="*50)
        print(f"!!! ERROR GENERAL CAPTURADO !!!")
        print(f"Tipo de Error: {type(e).__name__}")
        print(f"Mensaje de Error: {e}")
        print("="*50 + "\n")
        bot.reply_to(message, "❌ Lo siento, hubo un error general al intentar obtener la recomendación.")

    print("Mensaje de recomendación enviado.")

@bot.message_handler(commands=['recomendar'])
def send_recomendacion(message):

    user_topic = message.text.replace("/recomendar", "", 1).strip()

    # --- LÓGICA DE AUTOCOMPLETADO (Prompt para el usuario) ---
    if not user_topic:
        bot.reply_to(message, "🎧 Por favor, indica un tema o artista para la recomendación. Ejemplo: `/recomendar artistas similares a The Cure`")
        return

    try:
        instrucciones_keywords = (
            "Vas a recibir una solicitud de recomendación musical o de podcast. Tu tarea es generar las palabras clave ('keywords') MÁS ESPECÍFICAS posibles para buscar en Spotify. "
            "DEBES INCLUIR el tipo de contenido deseado dentro de las keywords. "
            "**REGLA CRÍTICA DE EXCLUSIÓN Y SIMILITUD:** Si el usuario pide artistas o playlists 'similares a X', las keywords deben centrarse SÓLO en el género, estilo y descripción de X (Ej: soul, R&B, jazz-funk, argentino) y tienen **PROHIBIDO INCLUIR EL NOMBRE DEL ARTISTA ORIGINAL (X) DE FORMA ABSOLUTA** para forzar una alternativa. Ejemplo: Si piden 'Nafta', usa 'bandas de soul/funk argentino contemporáneo' o 'playlist de R&B y jazz argentino'."
            "Elige el 'search_type' más relevante de la lista: 'track', 'playlist', 'album', 'artist', o 'podcast'."
        )

        resultado_keywords_json = preguntar_gemini(
            pregunta=f"Solicitud del usuario: {user_topic}",
            instrucciones=instrucciones_keywords,
            estructura_salida=RespuestaSpotify
        )

        resultado_keywords = json.loads(resultado_keywords_json)
        keywords = resultado_keywords["keywords"]
        search_type = resultado_keywords["search_type"]

        spotify_result = buscar_en_spotify(keywords, search_type=search_type)
        recomendacion_url = spotify_result.get("url")

        if not recomendacion_url:
             bot.reply_to(message, f"Lo siento, no encontré un resultado relevante en Spotify para la búsqueda '{keywords}'.")
             return

        instrucciones_respuesta_final = (
            "Vas a recibir la solicitud original del usuario, el tipo de contenido que querías sugerir ('Tipo de contenido sugerido') y un enlace de Spotify."
            "\n\n**TU TAREA PRINCIPAL ES GENERAR EL MENSAJE FINAL COMPLETO:**"
            "\n1. **Estilo:** La respuesta debe usar el **voseo** y tener un tono **amigable, informal y natural** (castellano rioplatense sin modismos exagerados). Debe sonar como un amigo."
            "\n2. **Identifica el Contenido Real:** Mira el enlace de Spotify para determinar qué tipo de contenido es realmente ('/track/'=canción, '/artist/'=artista, '/show/' o '/episode/'=podcast, '/playlist/'=playlist)."
            "\n3. **Genera el Comentario:** Crea un comentario de **dos a tres líneas de largo**. Este comentario DEBE hacer referencia al TIPO DE CONTENIDO REAL que identificaste en la URL."
            "\n   a) **Si el tipo de contenido REAL coincide con el sugerido:** Preséntalo de forma entusiasta."
            "\n   b) **Si el tipo de contenido REAL NO coincide:** Menciona el tema con un tono suave, explicando que encontró algo un poco diferente pero relevante."
            "\n4. **Formato Final:** La respuesta debe ser **UN ÚNICO BLOQUE DE TEXTO** que combine el comentario y el enlace de Spotify. NO añadas títulos ni repitas información."
        )

        respuesta = preguntar_gemini(
            pregunta=f"Solicitud original: {user_topic} \n Tipo de contenido sugerido: {search_type} \n Enlace de Spotify: {recomendacion_url}",
            instrucciones=instrucciones_respuesta_final
        )

        bot.reply_to(message, respuesta)

    except json.JSONDecodeError:
        bot.reply_to(message, "Hubo un error al procesar la respuesta de Gemini (formato JSON inválido).")
    except KeyError as e:
        bot.reply_to(message, f"Error: Faltó una clave esperada en el resultado. Clave faltante: {e}.")
    except Exception as e:
        print("\n" + "="*50)
        print(f"!!! ERROR GENERAL CAPTURADO !!!")
        print(f"Tipo de Error: {type(e).__name__}")
        print(f"Mensaje de Error: {e}")
        print("="*50 + "\n")
        bot.reply_to(message, "❌ Lo siento, hubo un error general al intentar obtener la recomendación.")

    print("Mensaje de recomendación enviado.")

@bot.message_handler(commands=['playlist'])
def send_playlist(message):

   try:

      #Primero pedimos a gemini que nos devuelva el nombre de la playlist y las canciones
      resultado_canciones = preguntar_gemini(pregunta=message.text, instrucciones="Vas a recibir un mensaje con varias canciones para crear una playlist, organiza las canciones en una lista de nombres de canciones y el nombre de la playlist creado por vos", estructura_salida=RespuestaPlaylist)

      #Luego parseamos el json que nos devuelve gemini a diccionario de python
      resultado_canciones = json.loads(resultado_canciones)

      #Ahora buscamos las canciones en api de spotify para conseguir sus urls
      canciones = [buscar_en_spotify(cancion)["url"] for cancion in resultado_canciones["canciones"]]

      #Creamos la playlist en spotify
      url = crear_playlist(resultado_canciones["nombre"], canciones)

      #Teniendo todo el contexto, gemini genera la respuesta final
      respuesta = preguntar_gemini(f"Mensaje original: {message.text} \n URL de la playlist: {url}", instrucciones="vas a recibir el mensaje original de un usuario que quería crear una playlist, respondé el mensaje original usando la url de la playlist")
      bot.reply_to(message, respuesta)
   except Exception :
      bot.reply_to(message, "Lo siento, hubo un error al crear la playlist")

   print("Mensaje enviado.")

# Iniciar el bot
print("Bot iniciado")
bot.polling()