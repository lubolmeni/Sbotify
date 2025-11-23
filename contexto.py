import telebot
from adapters.gemini_adapter import preguntar_gemini
import os
from dotenv import load_dotenv
import typing_extensions as typing
from adapters.spotify_adapter import buscar_en_spotify, crear_playlist 
import json

load_dotenv()

# Estructura de salida esperada de Gemini, similar a la usada en main.py
class RespuestaPlaylist(typing.TypedDict):
    nombre: str
    canciones: list[str] # Lista de búsquedas (keywords) para canciones

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(commands=['situación'])
def send_situacion_playlist(message):
    
    # Extraer la situación del usuario y limpiar el comando
    user_situation = message.text.replace("/situacion", "", 1).strip()

    if not user_situation:
        bot.reply_to(message, "💬 Por favor, describí la situación para la que querés la playlist. Ejemplo: `/situacion necesito música instrumental tranquila para estudiar concentrado`")
        return

    try:
        # --- 1. Petición a Gemini para generar el nombre y las búsquedas de canciones ---
        instrucciones_playlist = (
            "Vas a recibir una descripción de una situación específica (ej: estudiar, cocinar, viajar, etc.). "
            "Tu tarea es generar un nombre de playlist atractivo ('nombre') y una lista de 5 a 10 búsquedas de canciones ('canciones') "
            "que se adapten perfectamente al ambiente y ritmo de esa situación. Las 'canciones' deben ser búsquedas precisas (Ej: 'Jazz suave para concentración', 'Rock instrumental de los 90', 'pop optimista para limpiar')."
            "La salida debe seguir la estructura JSON provista."
        )
        
        resultado_canciones_json = preguntar_gemini(
            pregunta=f"Situación del usuario: {user_situation}",
            instrucciones=instrucciones_playlist,
            estructura_salida=RespuestaPlaylist
        )

        resultado_canciones = json.loads(resultado_canciones_json)
        playlist_nombre = resultado_canciones["nombre"]
        canciones_queries = resultado_canciones["canciones"]

        # --- 2. Buscar en Spotify por la URI de cada canción ---
        canciones_uris = []
        for query in canciones_queries:
            # Buscar el primer resultado de tipo 'track' (canción) para cada keyword
            spotify_result = buscar_en_spotify(query, search_type="track") 
            track_url = spotify_result.get("url")
            
            if track_url:
                # Se recolectan los URLs (que se asumen como URIs o son manejados por crear_playlist)
                canciones_uris.append(track_url)

        # Verificar si se encontraron tracks
        if not canciones_uris:
             bot.reply_to(message, f"❌ Lo siento, no pude encontrar canciones relevantes en Spotify para la situación: '{user_situation}'. Probá con una descripción más específica.")
             return

        # --- 3. Crear la playlist en Spotify ---
        url = crear_playlist(playlist_nombre, canciones_uris)

        # --- 4. Generar la respuesta final con Gemini ---
        instrucciones_respuesta_final = (
            "Vas a recibir la situación original de un usuario y el URL de una playlist de Spotify que se acaba de crear."
            "\n\n**TU TAREA PRINCIPAL ES GENERAR EL MENSAJE FINAL COMPLETO:**"
            "\n1. **Estilo:** La respuesta debe usar el **voseo** y tener un tono **amigable, informal y entusiasta**. Agregá emojis para hacerlo más canchero."
            "\n2. **Contenido:** Generá un mensaje de **dos a tres líneas** que confirme que la playlist se creó, mencione el nombre que se le puso y que invite al usuario a disfrutar de la música para su situación."
            "\n3. **Formato Final:** La respuesta debe ser UN ÚNICO BLOQUE DE TEXTO que combine el comentario y contenga el URL de la playlist de forma clara."
        )

        respuesta = preguntar_gemini(
            pregunta=f"Situación original: {user_situation} \n Nombre de la playlist: {playlist_nombre} \n URL de la playlist: {url}",
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
        bot.reply_to(message, "❌ Lo siento, hubo un error general al intentar crear la playlist para tu situación. Revisá la consola para más detalles.")

    print("Mensaje de playlist enviado.")

print("Bot iniciado")
bot.polling()
