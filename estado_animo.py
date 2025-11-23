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

@bot.message_handler(commands=['animo']) 
def send_welcome(message):
    
    user_mood = message.text.replace("/animo", "", 1).strip()

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

print("Bot iniciado")
bot.polling()