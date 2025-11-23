import telebot
from adapters.gemini_adapter import preguntar_gemini
import os
from dotenv import load_dotenv
import typing_extensions as typing
from adapters.spotify_adapter import buscar_en_spotify 
import json

load_dotenv()

class RespuestaSpotify(typing.TypedDict):
    keywords: str 
    search_type: typing.Literal["track", "playlist", "album", "artist", "podcast"] 

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(commands=['recomendar']) 
def send_recomendacion(message):
    
    user_topic = message.text.replace("/recomendar", "", 1).strip()

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

print("Bot iniciado")
bot.polling()