import time
from telebot import types
from datetime import datetime
from excepciones.excepcion_fecha_futura import ExceptionFechaFutura
from functools import wraps
import json
import requests
from procesadores.procesador_nlp import NLPProcessor, MenstrualNLPProcessor


class Router:
    def __init__(self, bot, nlp, imagen_analyzer, cycle_tracker, audio_analyzer, sentiment_analyzer):
        self.bot = bot
        self.nlp = nlp
        self.imagen_analyzer = imagen_analyzer
        self.audio_analyzer = audio_analyzer
        self.cycle_tracker = cycle_tracker
        self.sentiment_analyzer = sentiment_analyzer
        self.modos= {}
        self._registrar_rutas()

    # ============================
    # MENU PRINCIPAL
    # ============================
    def _mostrar_menu(self, chat_id):
        teclado = types.InlineKeyboardMarkup()
        botones = [
            types.InlineKeyboardButton("Quiero hablar de cómo me siento", callback_data="sentimientos"),
            types.InlineKeyboardButton("Mi cuerpo y mis síntomas", callback_data="sintomas"),
            types.InlineKeyboardButton("Registrar mi ciclo", callback_data="ciclo"),
            types.InlineKeyboardButton("Sorprendeme 💫", callback_data="sorpresa")
  
        ]
        teclado.add(*botones)

        self.bot.send_message(
            chat_id,
            "🌸 *MENÚ PRINCIPAL*\n¡Elige una opción o comienza a chatear conmigo!",
            parse_mode="Markdown",
            reply_markup=teclado
        )

    # ============================
    # HANDLERS
    # ============================
    def _registrar_rutas(self):

        @self.bot.message_handler(commands=['start', 'help'])
        def menu(message):
            self.modos[message.chat.id] = "menu"
            self.bot.send_message(message.chat.id, "Hola, soy OvulAI, tu bot de confianza. Estoy acá para acompañarte y escucharte 💕Contame, ¿qué necesitás hoy?")
            self._mostrar_menu(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text.lower() in ["volver al menú", "🔙 volver al menú"])
        def volver_al_menu(message):
            chat_id = message.chat.id
            self.modos[chat_id] = "menu"

            markup_vacio = types.ReplyKeyboardRemove()
            self.bot.send_message(chat_id, "🔙 Volviendo al menú principal...", reply_markup=markup_vacio)

            self._mostrar_menu(chat_id)



    # ============================
    # MENU PRINCIPAL
    # ============================
    def _mostrar_menu(self, chat_id):
        teclado = types.InlineKeyboardMarkup()
        botones = [
            types.InlineKeyboardButton("Quiero hablar de cómo me siento", callback_data="sentimientos"),
            types.InlineKeyboardButton("Mi cuerpo y mis síntomas", callback_data="sintomas"),
            types.InlineKeyboardButton("Registrar mi ciclo", callback_data="ciclo"),
            types.InlineKeyboardButton("Sorprendeme 💫", callback_data="sorpresa")
  
        ]
        teclado.add(*botones)

        self.bot.send_message(
            chat_id,
            "🌸 *MENÚ PRINCIPAL*\n¡Elige una opción o comienza a chatear conmigo!",
            parse_mode="Markdown",
            reply_markup=teclado
        )

    # ============================
    # HANDLERS
    # ============================
    def _registrar_rutas(self):

        @self.bot.message_handler(commands=['start', 'help'])
        def menu(message):
            self.modos[message.chat.id] = "menu"
            self.bot.send_message(message.chat.id, "Hola, soy OvulAI, tu bot de confianza. Estoy acá para acompañarte y escucharte 💕Contame, ¿qué necesitás hoy?")
            self._mostrar_menu(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text in [
            "volver al menú", "🔙 Volver al menú"])
        def volver_al_menu(message):
            chat_id = message.chat.id
            self.modos[chat_id] = "menu"
            self._mostrar_menu(chat_id)

        @self.bot.callback_query_handler(func=lambda call: call.data in["sentimientos", "sintomas", "ciclo", "sorpresa", "volver_menu"])
        def manejar_click_boton(call):
            chat_id = call.message.chat.id

            if call.data == "volver_menu":
                self.modos[chat_id] = "menu"
                self._mostrar_menu(chat_id)
                return
            
            if call.data == "sentimientos":
                self.modos[chat_id] = "sentimientos"
                self._mostrar_boton_volver(chat_id, "¡Hablemos de cómo te sentís! Estoy para escucharte.")
                self.bot.register_next_step_handler(call.message, self._procesar_sentimiento)

            elif call.data == "ciclo":
                self.modos[chat_id] = "ciclo"
                self._mostrar_boton_volver(chat_id, "📅 Escribí la fecha de tu último período (DD/MM/AAAA).")
                self.bot.register_next_step_handler(call.message, self._procesar_fecha_ciclo)
                fase = self.cycle_tracker.calcular_estado(str(call.message.chat.id))['fase']

            elif call.data == "sintomas":
                self.modos[chat_id] = "sintomas"
                self._mostrar_sintomas(chat_id)
                self.bot.register_next_step_handler(call.message, self._dar_recomendaciones_fase)


            elif call.data == "sorpresa":
                self.modos[chat_id] = "sorpresa"
                imagen = self.obtener_foto_random(chat_id)
                if imagen:
                    if imagen.endswith((".jpg", ".jpeg", ".png")):
                        self.bot.send_photo(chat_id, imagen, caption="¡Aquí tienes una sorpresa para alegrar tu día! 🐶")
                    elif imagen.endswith(".gif"):
                        self.bot.send_animation(chat_id, imagen, caption="¡Aquí tienes una sorpresa para alegrar tu día! 🐶")
                    elif imagen.endswith((".mp4", ".webm")):
                        self.bot.send_video(chat_id, imagen, caption="¡Aquí tienes una sorpresa para alegrar tu día! 🐶")
                    else: 
                        self.bot.send_photo(chat_id, imagen, caption="¡Aquí tienes una sorpresa para alegrar tu día! 🐶")
                else:
                    self.bot.send_message(chat_id, "¡No pude conseguir una foto esta vez, pero pronto lo intentaré de nuevo! 🐶")
                self.modos[chat_id] = "menu"

        @self.bot.message_handler(content_types=['photo'])
        def manejar_imagen(message):
            file_id = message.photo[-1].file_id
            file_info = self.bot.get_file(file_id)
            file_bytes = self.bot.download_file(file_info.file_path)
            img_b64 = self.imagen_analyzer.imagen_a_base64(file_bytes)
            descripcion = self.imagen_analyzer.describir_imagen(img_b64)
            self.bot.reply_to(message, descripcion or "No pude describir la imagen.")

        @self.bot.message_handler(content_types=['voice'])
        def manejar_audio(message):
            transcripcion = self.audio_analyzer.transcribir_voz_groq(message)
            if transcripcion:
                respuesta = self.audio_analyzer.obtener_respuesta_groq(transcripcion)
                self.bot.reply_to(message, respuesta or "No pude procesar tu mensaje de voz.")
            else:
                self.bot.reply_to(message, "No pude transcribir tu mensaje de voz.")

        @self.bot.message_handler(func=lambda msg: True)
        def responder(message):
            chat_id = message.chat.id
            modo = self.modos.get(chat_id, "menu")

            if modo == "sentimientos":
                self._procesar_sentimiento(message)
            elif modo == "ciclo":
                self._procesar_fecha_ciclo(message)
            elif modo == "menu":
                respuesta = self.nlp.buscar_en_dataset(message.text)
                self.bot.reply_to(message, respuesta or "No encontré una respuesta exacta 😥. Probá con otra pregunta.")
            else:
                self._mostrar_menu(chat_id)

    def _dar_recomendaciones_fase(self, message):
        chat_id = message.chat.id
        estado = self.cycle_tracker.calcular_estado(str(chat_id))

        if message.text.lower() in ["volver al menú", "🔙 volver al menú"]:
            self.modos[chat_id] = "menu"
            markup_vacio = types.ReplyKeyboardRemove()
            self.bot.send_message(chat_id, "🔙 Volviendo al menú principal...", reply_markup=markup_vacio)
            self._mostrar_menu(chat_id)
            return

        if not estado:
            self.bot.reply_to(message, "No tengo datos de tu ciclo. Registrá tu última menstruación para recibir recomendaciones.")
            return

        fase = estado["fase"]

        procesador_recomendaciones = MenstrualNLPProcessor("dt_recomendaciones.json", fase)
        texto_usuario = message.text

        respuesta = procesador_recomendaciones.buscar_en_dataset(texto_usuario, umbral=0.6)

        if respuesta:
            self.bot.reply_to(message, respuesta)
        else:
            self.bot.reply_to(message, "No tengo una respuesta para esta consulta específica. ¿Hay algo más con lo que pueda ayudarte?")

        self.bot.register_next_step_handler(message, self._dar_recomendaciones_fase)

    # ============================
    # BOTÓN VOLVER
    # ============================
    def _mostrar_boton_volver(self, chat_id, mensaje):
        teclado = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        boton_volver = types.KeyboardButton("🔙 Volver al menú")
        teclado.add(boton_volver)
        self.bot.send_message(chat_id, mensaje, reply_markup=teclado)
  
    # ============================
    # FUNCIONALIDADES
    # ============================
    def _procesar_sentimiento(self, message):
        try:
            texto = message.text.strip()
            respuesta = self.sentiment_analyzer.analizar_sentimiento(texto)
            self.bot.reply_to(message, respuesta)
        except Exception as e:
            print(f"⚠️ Error al analizar sentimiento: {e}")
            self.bot.reply_to(message, "Hubo un error al analizar tu mensaje 😕. Probá de nuevo.")
            self.bot.register_next_step_handler(message, self._procesar_sentimiento)

    def _procesar_fecha_ciclo(self, message):
        chat_id = str(message.chat.id)
        try:
            fecha = ExceptionFechaFutura.validar_fecha(message.text.strip())
            self.cycle_tracker.registrar_fecha(chat_id, fecha)
            estado = self.cycle_tracker.calcular_estado(chat_id)
            self.bot.reply_to(message, f"¡Fecha registrada! Estás en la fase: '{estado['fase']}'. Para más info, por favor volvé al menú y seleccioná 'Mi cuerpo y mis síntomas' 🌼🩷.")
            self.modos[int(chat_id)] = "menu"
            self._mostrar_menu(int(chat_id))

        except ValueError:
            self.bot.reply_to(message, "⚠️ Formato inválido. Usá DD/MM/AAAA.")
            self.bot.register_next_step_handler(message, self._procesar_fecha_ciclo)
        except ExceptionFechaFutura:
            self.bot.reply_to(message, "⚠️ La fecha no puede ser futura.")
            self.bot.register_next_step_handler(message, self._procesar_fecha_ciclo)
    
    def _mostrar_sintomas(self, chat_id):
        estado = self.cycle_tracker.calcular_estado(str(chat_id))
        if estado:
            intro = f"¡Te cuento cómo va tu ciclo, estás en fase '{estado['fase']}' 🌼!"
            mensaje = self.cycle_tracker.generar_mensaje(str(chat_id))
            if "Menstruación" in estado['fase']:
                respuesta = "Tu cuerpo está en un proceso de renovación. Date permiso para descansar 🌙"
            elif "Fase folicular" in estado['fase']:
                respuesta = "¡Es momento de nuevos comienzos! Tu energía está en aumento 🌱"
            elif "Ovulación" in estado['fase']:
                respuesta = "¡Estás en tu punto más radiante! Aprovechá esta energía creativa 🌸"
            else:
                respuesta = "Es tiempo de reflexión y autocuidado 🌕"
        else:
            intro = "╭🌷━━━━━━━━━━━🌷╮"
            mensaje = "Todavía no registraste tu última fecha de ciclo 🌸\nPodés hacerlo con el botón 'Registrar mi ciclo' 📅"
            respuesta = "Te mando una frase motivadora: 'Sos más fuerte de lo que pensás.' 🌷"
            self._mostrar_boton_volver(chat_id, f"{intro}\n\n{mensaje}\n\n{respuesta}")
            return

        self._mostrar_boton_volver(chat_id, f"{intro}\n\n{mensaje}\n\n{respuesta}")

    def obtener_foto_random(self, chat_id):
        try:
            while True:
                resp = requests.get("https://random.dog/woof.json")
                data = resp.json()
                imagen = data.get("url")
                if imagen.endswith((".jpg", ".jpeg", ".png", ".gif", ".mp4", ".webm")):
                        break
            return imagen
        except Exception:
                return None