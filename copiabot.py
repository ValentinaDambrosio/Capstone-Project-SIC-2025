#Bot telegram, tener en cuenta para el CAPSTONE
import os
import json
import base64
import requests
import telebot
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from NLP import comparar_texto
from datetime import datetime, timedelta


nltk.download('stopwords')

TOKEN_TELEGRAM = os.getenv('TELEGRAM_TOKEN', '7640771173:AAGGmaB6mu-dKg4cBE6_qqS27tpFZcRrPlk')
GROQ_APIKEY = os.getenv('GROQ_TOKEN', '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')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
PATH_JSON = 'datasettt.json'

bot = telebot.TeleBot(TOKEN_TELEGRAM)

ARCHIVO_CICLOS = "ciclos.json"
registro_periodos = {}

# ---------------------- Dataset ----------------------

def cargar_dataset():
    try:
        with open(PATH_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def buscar_en_dataset(pregunta, dataset, umbral=0.5):
    dataset_textos = [item["pregunta"] for item in dataset]
    respuesta_texto, score = comparar_texto(pregunta, dataset_textos)
    if score >= umbral:
        for item in dataset:
            if item["pregunta"] == respuesta_texto:
                return item["respuesta"]
    return None


dataset = cargar_dataset()


# ---------------------- Groq Texto ----------------------

def respuesta_groq(mensaje):
    headers = {
        "Authorization": f"Bearer {GROQ_APIKEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": mensaje}]
    }

    try:
        resp = requests.post(GROQ_URL, headers=headers, json=data, timeout=20)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
        else:
            return f"Error Groq: {resp.status_code}"
    except Exception as e:
        return f"Error identificado como {e}"


# ---------------------- Groq Imagen ----------------------

def imagen_a_base64(ruta_o_bytes_imagen):
    try:
        if isinstance(ruta_o_bytes_imagen, bytes):
            return base64.b64encode(ruta_o_bytes_imagen).decode('utf-8')
        else:
            with open(ruta_o_bytes_imagen, "rb") as archivo_imagen:
                return base64.b64encode(archivo_imagen.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al convertir imagen a base64: {e}")
        return None


def describir_imagen_con_groq(imagen_base64):
    headers = {
        "Authorization": f"Bearer {GROQ_APIKEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Por favor, describe esta imagen de manera detallada y clara en español. "
                            "Incluye todos los elementos importantes que veas, colores, objetos, personas, "
                            "acciones, emociones y cualquier detalle relevante."
                            "si encuentras alguna relación con el ciclo menstrual, menciona en qué y de ser necesario aconseja al usuario al respecto"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}
                    }
                ]
            }
        ],
        "temperature": 1.5,
        "max_tokens": 2000
    }

    try:
        resp = requests.post(GROQ_URL, headers=headers, json=data, timeout=40)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            return f"Error Groq Imagen: {resp.status_code}"
    except Exception as e:
        print(f"Error al describir imagen con Groq: {e}")
        return None

#.......................Ciclo............................

def guardar_datos_ciclos():
    try:
        with open(ARCHIVO_CICLOS, "w", encoding="utf-8") as f:
            json.dump(registro_periodos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar datos de ciclos: {e}")

def cargar_datos_ciclos():
    global registro_periodos
    if not os.path.exists(ARCHIVO_CICLOS):
        registro_periodos = {}
        guardar_datos_ciclos()
    else:
        try:
            with open(ARCHIVO_CICLOS, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                if contenido:
                    registro_periodos = json.loads(contenido)
                else:
                    registro_periodos = {}
        except Exception as e:
            print(f"⚠️ Error al cargar datos de ciclos: {e}")
            registro_periodos = {}

cargar_datos_ciclos()

# ---------------------- Comando /ciclo ----------------------
@bot.message_handler(commands=['ciclo'])
def registrar_periodo(message):
    chat_id = str(message.chat.id)
    if chat_id in registro_periodos:
        fecha_guardada = datetime.strptime(registro_periodos[chat_id], "%Y-%m-%d")
        hoy = datetime.now()
        dias_desde = (hoy - fecha_guardada).days
        duracion_ciclo = 28
        ciclos_pasados = dias_desde // duracion_ciclo
        dia_ciclo = (dias_desde % duracion_ciclo) + 1  # día dentro del ciclo
        proximo = fecha_guardada + timedelta(days=(ciclos_pasados + 1) * duracion_ciclo)
        dias_restantes = (proximo - hoy).days

        # Determinar fase
        if 1 <= dia_ciclo <= 5:
            fase = "Menstruación 🩸"
        elif 6 <= dia_ciclo <= 13:
            fase = "Fase folicular 🌱"
        elif 14 <= dia_ciclo <= 16:
            fase = "Ovulación 🌸"
        else:
            fase = "Fase lútea 🌕"

        respuesta = (
            f"🩷 Último período: {fecha_guardada.strftime('%d/%m/%Y')}\n"
            f"⏱️ Día del ciclo: {dia_ciclo}\n"
            f"💫 Fase actual: {fase}\n"
            f"📅 Próximo período estimado: {proximo.strftime('%d/%m/%Y')} ({dias_restantes} días restantes)"
        )
        bot.reply_to(message, respuesta)
    else:
        bot.reply_to(message, "🩸 Escribí la **fecha de tu último período** (DD/MM/AAAA).\nEjemplo: `10/10/2025`")
        bot.register_next_step_handler(message, guardar_fecha_periodo)


def guardar_fecha_periodo(message):
    chat_id = str(message.chat.id)
    texto = message.text.strip()
    try:
        fecha = datetime.strptime(texto, "%d/%m/%Y")
        registro_periodos[chat_id] = fecha.strftime("%Y-%m-%d")
        guardar_datos_ciclos()

        hoy = datetime.now()
        dias_desde = (hoy - fecha).days
        duracion_ciclo = 28
        dia_ciclo = (dias_desde % duracion_ciclo) + 1

        # Determinar fase
        if 1 <= dia_ciclo <= 5:
            fase = "Menstruación 🩸"
        elif 6 <= dia_ciclo <= 13:
            fase = "Fase folicular 🌱"
        elif 14 <= dia_ciclo <= 16:
            fase = "Ovulación 🌸"
        else:
            fase = "Fase lútea 🌕"

        proximo = fecha + timedelta(days=28)
        dias_restantes = (proximo - hoy).days

        mensaje = (
            f"✅ Fecha registrada: {fecha.strftime('%d/%m/%Y')}\n"
            f"💫 Fase actual: {fase}\n"
            f"📅 Próximo período estimado: {proximo.strftime('%d/%m/%Y')} ({dias_restantes} días restantes)"
        )
        bot.reply_to(message, mensaje)

    except ValueError:
        bot.reply_to(message, "⚠️ Formato inválido. Usá DD/MM/AAAA. Ejemplo: `15/10/2025`")
        bot.register_next_step_handler(message, guardar_fecha_periodo)

#----------------------------------------------------------

# ---------------------- Comando /borrar_ciclo ----------------------

@bot.message_handler(commands=['borrar_ciclo'])
def borrar_ciclo(message):
    chat_id = str(message.chat.id)
    if chat_id in registro_periodos:
        del registro_periodos[chat_id]
        guardar_datos_ciclos()
        bot.reply_to(message, "🗑️ Tu registro de ciclo ha sido eliminado correctamente. Puedes registrar uno nuevo con /ciclo.")
    else:
        bot.reply_to(message, "⚠️ No tienes ningún registro de ciclo guardado.")


# ---------------------- Telegram: Menú Principal ----------------------

from telebot import types

@bot.message_handler(commands=['start', 'help'])
def bienvenida(message):
    # Crear teclado de opciones
    teclado = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    botones = [
        "1️⃣ Hoy quiero hablar de cómo me siento",
        "2️⃣ Catarsis time",
        "3️⃣ Necesito relajarme",
        "4️⃣ Ciclo y emociones",
        "5️⃣ Mi cuerpo y mis síntomas",
        "6️⃣ Tips de autocuidado",
        "7️⃣ Registrar mi día",
        "8️⃣ Sorprendeme 💫"
    ]

    # Agregar los botones al teclado
    for b in botones:
        teclado.add(types.KeyboardButton(b))

    # Enviar mensaje con el teclado adjunto
    bot.send_message(
        message.chat.id,
        "🌸 *MENÚ PRINCIPAL*\nSeleccioná una opción:",
        parse_mode="Markdown",
        reply_markup=teclado
    )


# ---------------------- Manejo de opciones del menú ----------------------

@bot.message_handler(func=lambda message: message.text in [
    "1️⃣ Hoy quiero hablar de cómo me siento",
    "2️⃣ Catarsis time",
    "3️⃣ Necesito relajarme",
    "4️⃣ Ciclo y emociones",
    "5️⃣ Mi cuerpo y mis síntomas",
    "6️⃣ Tips de autocuidado",
    "7️⃣ Registrar mi día",
    "8️⃣ Sorprendeme 💫"
])
def manejar_menu(message):
    opcion = message.text

    if opcion == "1️⃣ Hoy quiero hablar de cómo me siento":
        bot.reply_to(message, "💬 Contame, ¿cómo te sentís hoy?")
    elif opcion == "2️⃣ Catarsis time":
        bot.reply_to(message, "😮‍💨 Este es tu espacio de catarsis. Podés desahogarte libremente.")
    elif opcion == "3️⃣ Necesito relajarme":
        bot.reply_to(message, "🧘 Acá van algunas ideas para relajarte: respiración, música tranquila, o escribir lo que sentís.")
    elif opcion == "4️⃣ Ciclo y emociones":
        bot.reply_to(message, "🌕 Tu ciclo puede influir en cómo te sentís. Probá usar /ciclo para registrarlo o ver en qué fase estás.")
    elif opcion == "5️⃣ Mi cuerpo y mis síntomas":
        bot.reply_to(message, "💡 Contame qué síntomas estás notando para ayudarte a entenderlos mejor.")
    elif opcion == "6️⃣ Tips de autocuidado":
        bot.reply_to(message, "💅 Algunos tips de autocuidado: dormí bien, comé algo rico, movete un poco y tomate tu tiempo 💕.")
    elif opcion == "7️⃣ Registrar mi día":
        bot.reply_to(message, "📓 Escribí cómo fue tu día para guardarlo en tu registro personal.")
    elif opcion == "8️⃣ Sorprendeme 💫":
        bot.reply_to(message, "✨ Te mando una frase motivadora: *'Sos más fuerte de lo que pensás.'* 🌷")

# ---------------------- Manejo de mensajes e imágenes ----------------------
@bot.message_handler(content_types=['photo'])
def manejar_imagen(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)
        imagen_b64 = imagen_a_base64(file_bytes)
        descripcion = describir_imagen_con_groq(imagen_b64)
        bot.reply_to(message, descripcion or "No pude describir la imagen.")
    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error al procesar la imagen: {e}")

@bot.message_handler(func=lambda message: True)
def responder(message):
    pregunta = message.text
    respuesta = buscar_en_dataset(pregunta, dataset)
    if respuesta:
        bot.reply_to(message, respuesta)
    else:
        respuesta_con_ia = respuesta_groq(pregunta)
        bot.reply_to(message, respuesta_con_ia)


if __name__ == "__main__":
    print("Bot inicializado, esperando su mensaje :)...")
    # Asegurarnos de eliminar cualquier webhook previo que pueda bloquear el polling
    try:
        bot.remove_webhook()
        print("Webhook eliminado (si existía). Iniciando polling...")
    except Exception as e:
        print(f"Advertencia al eliminar webhook: {e}")

    # Iniciar polling para recibir mensajes (usa reconexión automática internamente)
    bot.infinity_polling()
