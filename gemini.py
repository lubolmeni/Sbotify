


import telebot
import google.generativeai as genai
import os

# Coloca tu token de bot aquí
bot = telebot.TeleBot('')


# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
   bot.reply_to(message, "¡Hola! Soy tu bot de prueba. Envíame un mensaje para ver cómo respondo.")


# Comando /help
@bot.message_handler(commands=['help'])
def send_help(message):
   bot.reply_to(message, "Escribe cualquier cosa y te responderé. Usa /start para comenzar.")


# Manejo de mensajes de texto
@bot.message_handler(func=lambda message: True)
def echo_all(message):
   bot.reply_to(message, f"Dijiste: {message.text}")


# Iniciar el bot
print("Bot iniciado")
bot.polling()


os.environ["API_KEY"] = "" #Se consigue acá https://aistudio.google.com/app/apikey
genai.configure(api_key=os.environ["API_KEY"])

model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("¿Por qué programar es divertido?")
print(response.text)

