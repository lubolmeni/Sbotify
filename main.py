import telebot
from adapters.gemini_adapter import preguntar_gemini
import os
from dotenv import load_dotenv
import typing_extensions as typing
from adapters.spotify_adapter import crear_playlist, buscar_en_spotify
import json
load_dotenv()

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(commands=['playlist'])
def send_playlist(message):

   #Mensaje de respuesta formato json de Gemini
   class RespuestaPlaylist(typing.TypedDict):
      nombre: str
      canciones: list[str]

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

