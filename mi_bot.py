import telebot


bot = telebot.TeleBot ("")
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "¡Hola! Soy tu primer bot")
bot.infinity_polling()

TOKEN=""

# Coloca tu token de bot aquí
bot = telebot.TeleBot(TOKEN)

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
bot.polling()

TOKEN=""

from telebot import types


bot = telebot.TeleBot(TOKEN)

# Comando /start para mostrar el menú inicial
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("Información")
    btn2 = types.KeyboardButton("Ayuda")
    btn3 = types.KeyboardButton("Contacto")
    btn4 = types.KeyboardButton("Opciones avanzadas")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "¡Bienvenido! Escoge una opción:", reply_markup=markup)

# Respuesta a cada opción del menú
@bot.message_handler(func=lambda message: True)
def menu_response(message):
    if message.text == "Información":
        bot.reply_to(message, "Aquí tienes información útil sobre el bot.")
    elif message.text == "Ayuda":
        bot.reply_to(message, "Estoy aquí para ayudarte. ¿En qué necesitas asistencia?")
    elif message.text == "Contacto":
        bot.reply_to(message, "Puedes contactarnos en: contacto@miempresa.com")
    elif message.text == "Opciones avanzadas":
        # Crea otro conjunto de botones para opciones avanzadas
        advanced_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        back_button = types.KeyboardButton("Regresar al menú principal")
        advanced_markup.add(back_button)
        bot.send_message(message.chat.id, "Opciones avanzadas:", reply_markup=advanced_markup)
    elif message.text == "Regresar al menú principal":
        send_welcome(message)
    else:
        bot.reply_to(message, "Por favor, selecciona una opción válida.")

# Iniciar el bot
bot.polling()

TOKEN=""

import requests


bot = telebot.TeleBot(TOKEN)

# Comando /start para mostrar el menú inicial
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("Información")
    btn2 = types.KeyboardButton("Generar Texto")
    btn3 = types.KeyboardButton("Contacto")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "¡Bienvenido! Escoge una opción:", reply_markup=markup)

# Respuesta a cada opción del menú
@bot.message_handler(func=lambda message: True)
def menu_response(message):
    if message.text == "Información":
        bot.reply_to(message, "Aquí tienes información útil sobre el bot.")
    elif message.text == "Generar Texto":
        bot.reply_to(message, "Generando texto aleatorio...")
        generate_random_text(message)
    elif message.text == "Contacto":
        bot.reply_to(message, "Puedes contactarnos en: contacto@miempresa.com")
    else:
        bot.reply_to(message, "Por favor, selecciona una opción válida.")

# Función para obtener texto aleatorio de FakerAPI
def generate_random_text(message):
    try:
        url = "https://fakerapi.it/api/v2/texts?_locale=es_ES&_quantity=1&_characters=200"
        response = requests.get(url)
        data = response.json()

        # Verificamos que la respuesta tiene el formato esperado
        if "data" in data and data["data"]:
            random_text = data["data"][0]["content"]
            bot.reply_to(message, f"Aquí tienes un texto aleatorio:\n\n{random_text}")
        else:
            bot.reply_to(message, "Lo siento, no se pudo obtener el texto aleatorio.")
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error al intentar obtener el texto aleatorio.")

# Iniciar el bot
bot.polling()
