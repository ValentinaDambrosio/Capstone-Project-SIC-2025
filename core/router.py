import time
from core.configuracion import Configuracion
from telebot import types
from datetime import datetime
from excepciones.excepciones_fechas import ExceptionFechas
import random
from functools import wraps
import json
import requests
from procesadores.procesador_nlp import NLPProcessor, MenstrualNLPProcessor
from core.google_calendario import GoogleCalendarClient
from deep_translator import GoogleTranslator as Translator

class Router:
    def __init__(self, bot, nlp, imagen_analyzer, cycle_tracker, audio_analyzer, sentiment_analyzer, google_auth):
        self.bot = bot
        self.nlp = nlp
        self.imagen_analyzer = imagen_analyzer
        self.audio_analyzer = audio_analyzer
        self.cycle_tracker = cycle_tracker
        self.sentiment_analyzer = sentiment_analyzer
        self.google_auth = google_auth
        self.google_calendar = GoogleCalendarClient(self.google_auth.token_storage)
        self.modos= {}
        self._registrar_rutas()
        
    # ============================
    # MENU PRINCIPAL
    # ============================
    def _mostrar_menu(self, chat_id):
        teclado = types.InlineKeyboardMarkup(row_width=1)
        botones = [
            types.InlineKeyboardButton("Quiero hablar de cómo me siento", callback_data="sentimientos"),
            types.InlineKeyboardButton("Mi cuerpo y mis síntomas", callback_data="sintomas"),
            types.InlineKeyboardButton("Registrar mi ciclo", callback_data="ciclo"),
            types.InlineKeyboardButton("Conectar mi calendario", callback_data="google_auth"),
            types.InlineKeyboardButton("Sorprendeme 💫", callback_data="sorpresa"),
            types.InlineKeyboardButton("Información OvulAI", callback_data="info")
  
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

        @self.bot.callback_query_handler(func=lambda call: call.data in["sentimientos", "sintomas", "ciclo", "sorpresa", "volver_menu", "google_auth", "info"])
        def manejar_click_boton(call):
            chat_id = call.message.chat.id

            if call.data == "volver_menu":
                self.modos[chat_id] = "menu"
                self._mostrar_menu(chat_id)
                return
            
            if call.data == "sentimientos":
                self.modos[chat_id] = "sentimientos"
                self._mostrar_boton_volver(chat_id, "💕¡Hablemos de cómo te sentís! Estoy para escucharte.")
                self.bot.register_next_step_handler(call.message, self._procesar_sentimiento)

            elif call.data == "ciclo":
                self.modos[chat_id] = "ciclo"
                self._mostrar_boton_volver(chat_id, "📅 Escribí la fecha de tu último período (DD/MM/AAAA).")
                self.bot.register_next_step_handler(call.message, self._procesar_fecha_ciclo)
                estado_temp = self.cycle_tracker.calcular_estado(str(call.message.chat.id))
                if estado_temp:
                    fase = estado_temp.get('fase')

            elif call.data == "sintomas":
                self.modos[chat_id] = "sintomas"
                self._mostrar_sintomas(chat_id)
                self.bot.register_next_step_handler(call.message, self._dar_recomendaciones_fase)

            elif call.data =="google_auth":
                # Verifica si el usuario ya tiene tokens almacenados; si los tiene, informar y no generar link
                tokens = self.google_auth.obtener_tokens(str(chat_id))
                if tokens:
                    self.bot.send_message(
                        chat_id,
                        "✅ Tu cuenta de Google ya está conectada y sincronizada con el calendario."
                    )
                    self.modos[chat_id] = "menu"
                    self._mostrar_menu(chat_id)
                else:
                    link = self.google_auth.generar_link_autorizacion(chat_id)
                    self.bot.send_message(
                        chat_id,
                        f"Para conectar tu cuenta de Google y sincronizar tu ciclo con tu calendario, hacé click en el siguiente enlace:\n\n[🌷🔗 Conectar con mi calendario]({link})",
                        parse_mode = "Markdown"
                    )
                    self.modos[chat_id] = "menu"
                    self._mostrar_menu(chat_id)

            elif call.data == "sorpresa":
                self.modos[chat_id] = "sorpresa"
                self.bot.send_message(chat_id, "¡Genial! Preparando una sorpresa especial para vos... 💫")
                opciones = ["foto", "horoscopo", "frase"]
                opcion = random.choice(opciones)

                try:
                    # Leer horóscopo
                    if opcion == "horoscopo":
                        self.bot.send_message(chat_id, "Hoy toca: Tu horóscopo del día 🔮")
                        self.obtener_signo(call.message)
                        return
                    
                    # Enviar foto random de animales
                    elif opcion == "foto":
                        imagen = self.obtener_foto_random(chat_id)
                        captions = [
                            "¡Aquí tienes una sorpresa para alegrar tu día! 🐶",
                            "¡Mirá esta belleza! Espero que te saque una sonrisa 🩷",
                            "¡Un regalito visual para vos! Disfrutalo 🐾",
                            "¡Espero que esta imagen te alegre el día! 🌟",
                            "¡Una sorpresa especial solo para vos! 🐕"
                        ]
                        caption = random.choice(captions)

                        self.bot.send_message(chat_id, "Hoy toca: Imagen random de animalitos 🐾")

                        if imagen:
                            if imagen.endswith((".jpg", ".jpeg", ".png")):
                                self.bot.send_photo(chat_id, imagen, caption = caption)
                            elif imagen.endswith(".gif"):
                                self.bot.send_animation(chat_id, imagen, caption = caption)
                            elif imagen.endswith((".mp4", ".webm")):
                                self.bot.send_video(chat_id, imagen, caption = caption)
                            else: 
                                self.bot.send_photo(chat_id, imagen, caption = caption)
                        else:
                            self.bot.send_message(chat_id, "¡No pude conseguir una foto esta vez, pero pronto lo intentaré de nuevo! 😊")
                    else:
                        frase = self.obtener_frase_inspiradora()
                        self.bot.send_message(chat_id, "Hoy toca: Frase inspiradora 🪷")
                        self.bot.send_message(chat_id, frase, parse_mode="Markdown")

                except Exception as e:

                    print(f"⚠️ Error en opción sorpresa: {e}")
                    self.bot.send_message(chat_id, "Hubo un error al procesar tu solicitud 😕. Volviendo al menú principal.")
                
                self.modos[chat_id] = "menu"
                self._mostrar_menu(chat_id)
           
            elif call.data == "info":
                info_texto = (
                                "🌸 *Información sobre OvulAI* 🌸\n\n"
                                    "¡Hola! Soy *OvulAI*, tu asistente de confianza 💕. Estoy aquí para acompañarte en temas de emociones, autocuidado y seguimiento de tu ciclo menstrual.\n\n"
                                    "Conmigo podés:\n"
                                    "💬 Hablar de cómo te sentís y recibir consejos emocionales.\n"
                                    "📅 Registrar tu ciclo menstrual y obtener recomendaciones personalizadas según tu fase.\n"
                                    "🩷 Consultar sobre tu cuerpo y tus síntomas.\n"
                                    "💫 Sorprenderte con frases, horóscopos o imágenes que alegren tu día.\n\n"
                                    "🔗 También podés conectar tu calendario de Google para sincronizar tus ciclos.\n\n"
                                    "Recordá que estoy para escucharte y acompañarte, pero no reemplazo la atención profesional en salud mental o médica. Siempre cuidá de vos primero 💛."
                            )
                info_botones = (
                    "*¿Cómo funciona el menú? 🌷*\n\n"
                    "1️⃣ *Quiero hablar de cómo me siento*: Contame cómo te sentís y recibirás consejos emocionales personalizados.\n"
                    "2️⃣ *Mi cuerpo y mis síntomas*: Consultá sobre tu ciclo y obtené recomendaciones según tu fase menstrual.\n"
                    "3️⃣ *Registrar mi ciclo*: Guardá la fecha de tu última menstruación para recibir información personalizada.\n"
                    "4️⃣ *Conectar mi calendario*: Sincronizá tu ciclo con Google Calendar para recibir recordatorios.\n"
                    "5️⃣ *Sorprendeme 💫*: Recibí frases inspiradoras, horóscopos o imágenes para alegrar tu día.\n"
                    "6️⃣ *Información OvulAI*: Este mensaje que estás leyendo 😄.\n\n"
                    "💡 *Tips de uso*:\n"
                    "- Usá los botones del menú para navegar rápidamente.\n"
                    "- Podés volver al menú principal en cualquier momento con '🔙 Volver al menú'.\n"
                    "- Si escribís algo que no corresponde a los botones, no hay problema: buscaré en mi *dataset* si es un mensaje de texto o usaré la IA si se trata de audios o imágenes para darte una respuesta útil.\n"
                )
                self.bot.send_message(chat_id, info_texto, parse_mode = "Markdown")
                self.bot.send_message(chat_id, info_botones, parse_mode = "Markdown")
                self.bot.send_message(chat_id, "*¡Comencemos! 🪷*", parse_mode = "Markdown")
                self.modos[chat_id] = "menu"
                self._mostrar_menu(chat_id)


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
                respuesta = self.nlp.buscar_en_dataset(message.text, umbral = 0.7)
                self.bot.reply_to(message, respuesta or "No encontré una respuesta exacta en mi base de datos. Por favor, probá con otra pregunta.")
            else:
                self._mostrar_menu(chat_id)

    def _dar_recomendaciones_fase(self, message):
        chat_id = message.chat.id
        estado = self.cycle_tracker.calcular_estado(str(chat_id))

        if message.text is None:
            self.bot.reply_to(
                                message,
                                "Vi que enviaste algo que no es texto 💬. Por ahora solo puedo responder a consultas escritas sobre tu ciclo y síntomas. 🌸"
                            )
            self.bot.register_next_step_handler(message, self._dar_recomendaciones_fase)
            return
        
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

        respuesta = procesador_recomendaciones.buscar_en_dataset(texto_usuario, umbral=0.7)
        if respuesta:
            self.bot.reply_to(message, respuesta, parse_mode = "Markdown")
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
    # ============================
    #     MODO "SENTIMIENTOS"
    # ============================

    def _procesar_sentimiento(self, message):
        chat_id = message.chat.id
        try:
            if message.text is None:
                self.bot.reply_to(
                            message,
                            "Vi que enviaste algo que no es texto 💬. Por ahora solo puedo responder a mensajes escritos sobre cómo te sentís. 🌷"
                                )
                self.bot.register_next_step_handler(message, self._procesar_sentimiento)
                return
            
            if message.text.lower() in ["volver al menú", "🔙 volver al menú"]:
                self.modos[chat_id] = "menu"
                markup_vacio = types.ReplyKeyboardRemove()
                self.bot.send_message(chat_id, "🔙 Volviendo al menú principal...", reply_markup=markup_vacio)
                self._mostrar_menu(chat_id)
                return
            
            texto = message.text.strip()

            resultado = self.sentiment_analyzer.analizar_sentimiento(texto)

            respuesta_sentimiento = resultado.get("respuesta")
            sentimiento = resultado.get("sentimiento")
            confianza = resultado.get("confianza")

            consejos_emocionales = NLPProcessor("dt_consejos_emocionales.json")
            consejo = consejos_emocionales.buscar_en_dataset(texto, umbral=0.6)

            respuesta = f"{respuesta_sentimiento}\n\n{consejo}" if consejo else respuesta_sentimiento

            self.bot.reply_to(message, respuesta, parse_mode = "Markdown")

            if sentimiento == "NEG" and confianza > 0.95:
                self.mostrar_boton_psicologo(message.chat.id)

        except Exception as e:
            print(f"⚠️ Error al analizar sentimiento: {e}")
            self.bot.reply_to(message, "Hubo un error al analizar tu mensaje 😕. Probá de nuevo.")
            self.bot.register_next_step_handler(message, self._procesar_sentimiento)

    def mostrar_boton_psicologo(self, chat_id):
        mensaje = (
            "Si sentís que necesitás hablar con una profesional, podés contactar con un psicólogo. 💬\n\n"
            "📞 *Línea de Atención Psicológica:* 0800-222-3444\n\n"
            "Recordá que buscar ayuda es un acto de valentía y autocuidado 💛"
        )

        teclado = types.InlineKeyboardMarkup()
        boton_cercania = types.InlineKeyboardButton(
            text="💛 Buscar Psicólogos Cerca Mío",
            url="https://www.google.com/maps/search/psicologos+cerca+de+mi"
        )
        boton_online = types.InlineKeyboardButton(
            text="🌐 Psicólogos Online",
            url="https://www.terapiaweb.com.ar/"
        )
        teclado.add(boton_cercania)
        teclado.add(boton_online)

        self.bot.send_message(chat_id, mensaje, reply_markup=teclado, parse_mode="Markdown")

    # ============================
    #   MODO REGISTRAR CICLO
    # ============================

    def _procesar_fecha_ciclo(self, message):
        chat_id = str(message.chat.id)
        try:
            fecha = ExceptionFechas.validar_fecha(message.text.strip())
            self.cycle_tracker.registrar_fecha(chat_id, fecha)
            estado = self.cycle_tracker.calcular_estado(chat_id)
            self.bot.reply_to(message, f"¡Fecha registrada! Estás en la fase: '{estado['fase']}'. Para más info, por favor volvé al menú y seleccioná 'Mi cuerpo y mis síntomas' 🌼🩷.")
            
            if not self.google_auth.obtener_tokens(chat_id):
                self.bot.send_message(
                    chat_id,
                    "⚠️ Aún no conectaste tu cuenta de Google Calendar. "
                    "Podés hacerlo desde el menú principal con el botón 'Conectar con Google' 🔗"
                )
            else:
                proximo = self.google_calendar.crear_eventos_ciclo(chat_id, fecha)
                
            self.modos[int(chat_id)] = "menu"
            self._mostrar_menu(int(chat_id))

        except ValueError:
            self.bot.reply_to(message, "⚠️ Formato inválido. Usá DD/MM/AAAA.")
            self.bot.register_next_step_handler(message, self._procesar_fecha_ciclo)
        except ExceptionFechas as e:
            self.bot.reply_to(message, f"⚠️{e}")
            self.bot.register_next_step_handler(message, self._procesar_fecha_ciclo)
    
    # ============================
    #    MODO "SÍNTOMAS"
    # ============================
    
    def _mostrar_sintomas(self, chat_id):
        estado = self.cycle_tracker.calcular_estado(str(chat_id))
        
        if estado:
            intro = f"¡Te cuento cómo va tu ciclo, estás en fase '{estado['fase']}' 🌼!"
            mensaje = self.cycle_tracker.generar_mensaje(str(chat_id))

            # 💫 Recomendaciones más completas según fase
            if "Menstruación" in estado['fase']:
                respuesta = (
                    "💆‍♀️ *Tu cuerpo está en proceso de renovación.*\n"
                    "Podés sentirte con menos energía, así que priorizá el descanso, hidratate bien y escuchá lo que tu cuerpo necesita. "
                        "Un baño tibio o una infusión pueden ayudarte a relajarte. 🌙"
                )
            elif "Fase folicular" in estado['fase']:
                respuesta = (
                        "🌱 *Tu energía está creciendo nuevamente.*\n"
                        "Es el momento ideal para planificar, aprender algo nuevo o retomar actividades que te inspiren. "
                        "Tu cuerpo responde muy bien al movimiento y a las ideas frescas 💡."
                    )
            elif "Ovulación" in estado['fase']:
                respuesta = (
                        "🌸 *Estás en tu punto más radiante.*\n"
                        "Tu vitalidad, creatividad y confianza están al máximo. Aprovechá para hacer ejercicio intenso o conectar con los demás. "
                        "Recordá cuidarte si tenés relaciones sexuales: la protección es clave 🛡️."
                    )
            else:
                respuesta = (
                        "🌕 *Es momento de introspección y autocuidado.*\n"
                        "Podés notar más sensibilidad o cambios en el ánimo. Hacete espacio para actividades suaves: leer, meditar o hacer yoga. "
                        "Reducí el estrés y dormí bien 🫖."
                    )

            mensaje_final = f"{intro}\n\n{mensaje}\n\n{respuesta}"
        else:
            intro = "╭🌷━━━━━━━━━━━🌷╮"
            mensaje = "Todavía no registraste tu última fecha de ciclo 🌸\nPodés hacerlo con el botón 'Registrar mi ciclo' 📅"
            respuesta = "Te mando una frase motivadora: 'Sos más fuerte de lo que pensás.' 🌷"
            self._mostrar_boton_volver(chat_id, mensaje_final)
            return

        self._mostrar_boton_volver(chat_id, mensaje_final)

    # ============================
    #      MODO "SORPRESA"
    # ============================

    # ============================
    #     IMAGENES RANDOM
    # ============================
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

    # ============================
    #     HORÓSCOPO DEL DÍA
    # ============================
    def obtener_signo(self, message):
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id,
            "✨ Por favor, ingresá tu fecha de nacimiento en formato *DD/MM* o *DD/MM/AAAA* para saber tu signo zodiacal."
        )
        self.bot.register_next_step_handler(message, self._procesar_signo_zodiacal)

    def _procesar_signo_zodiacal(self, message):
        chat_id = message.chat.id
        fecha_str = message.text.strip()

        try:
            partes = fecha_str.split("/")
            if len(partes) == 2:
                fecha = datetime.strptime(fecha_str, "%d/%m")
            else:
                fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            self.bot.send_message(chat_id, f"⚠️ Escribí algo como *23/08* o *23/08/1998*.")
            self.bot.register_next_step_handler(message, self._procesar_signo_zodiacal)
            return

        dia, mes = fecha.day, fecha.month

        if (mes == 12 and dia >= 22) or (mes == 1 and dia <= 19):
            signo = "capricorn"
            español = "Capricornio"
        elif (mes == 1 and dia >= 20) or (mes == 2 and dia <= 18):
            signo = "aquarius"
            español = "Acuario"
        elif (mes == 2 and dia >= 19) or (mes == 3 and dia <= 20):
            signo = "pisces"
            español = "Piscis"
        elif (mes == 3 and dia >= 21) or (mes == 4 and dia <= 19):
            signo = "aries"
            español = "Aries"
        elif (mes == 4 and dia >= 20) or (mes == 5 and dia <= 20):
            signo = "taurus"
            español = "Tauro"
        elif (mes == 5 and dia >= 21) or (mes == 6 and dia <= 20):
            signo = "gemini"
            español = "Géminis"
        elif (mes == 6 and dia >= 21) or (mes == 7 and dia <= 22):
            signo = "cancer"
            español = "Cáncer"
        elif (mes == 7 and dia >= 23) or (mes == 8 and dia <= 22):
            signo = "leo"
            español = "Leo"
        elif (mes == 8 and dia >= 23) or (mes == 9 and dia <= 22):
            signo = "virgo"
            español = "Virgo"
        elif (mes == 9 and dia >= 23) or (mes == 10 and dia <= 22):
            signo = "libra"
            español = "Libra"
        elif (mes == 10 and dia >= 23) or (mes == 11 and dia <= 21):
            signo = "scorpio"
            español = "Escorpio"
        else:
            signo = "sagittarius"
            español = "Sagitario"

        self._mostrar_boton_volver(chat_id, f"🌟 Tu signo solar zodiacal es *{español}* 🌟")
        self.obtener_horoscopo(chat_id, signo)


    def obtener_horoscopo(self, chat_id, signo):
        url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={signo.lower()}&day=today"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()

            horoscopo_en = data["data"]["horoscope_data"] 

            horoscopo_es = Translator(source='en', target='es').translate(horoscopo_en)

            if horoscopo_es:
                self.bot.send_message(chat_id, f"🔮 Tu horóscopo para hoy es:\n\n{horoscopo_es}")
            else:
                self.bot.send_message(chat_id, "No pude obtener tu horóscopo en este momento.")
        except Exception as e:
            print(f"⚠️ Error al obtener horóscopo: {e}")
            self.bot.send_message(chat_id, "No pude obtener tu horóscopo en este momento.")

        self._mostrar_menu(chat_id) 

    # ============================
    #     FRASE INSPIRADORA
    # ============================

    def obtener_frase_inspiradora(self):
        url = "https://zenquotes.io/api/random"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()[0]
                frase_en = data["q"]
                frase_es = Translator(source='en', target='es').translate(frase_en)
                autor = data["a"]
                return f"🪷 *Frase del día:* “{frase_es}”\n— {autor}"
            else:
                return "No pude conseguir una frase por ahora 😕."
        except Exception as e:
            return f"Error al obtener frase: {e}"