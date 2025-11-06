from telebot import types
from datetime import datetime
from excepciones.excepcion_fecha_futura import FechaFutura

class Router:
    def __init__(self, bot, nlp, imagen_analyzer, cycle_tracker, audio_analyzer, sentiment_analyzer):
        self.bot = bot
        self.nlp = nlp
        self.imagen_analyzer = imagen_analyzer
        self.audio_analyzer = audio_analyzer
        self.cycle_tracker = cycle_tracker
        self.sentiment_analyzer = sentiment_analyzer
        self._registrar_rutas()

    def _registrar_rutas(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def menu(message):
            teclado = types.InlineKeyboardMarkup()
            botones = [
                types.InlineKeyboardButton("Quiero hablar de cómo me siento", callback_data="sentimientos"),
                types.InlineKeyboardButton("Mi cuerpo y mis síntomas", callback_data="sintomas"),
                types.InlineKeyboardButton("Registrar mi ciclo", callback_data="ciclo"),
                types.InlineKeyboardButton("Sorprendeme 💫", callback_data="sorpresa")
            ]

            teclado.add(*botones)

            self.bot.send_message(
                message.chat.id,
                "🌸 *MENÚ PRINCIPAL*\n¡Elige una opción o comienza a chatear conmigo!",
                parse_mode="Markdown",
                reply_markup=teclado
            )

        @self.bot.message_handler(func=lambda message: message.text in [
            "Quiero hablar de cómo me siento",
            "Mi cuerpo y mis síntomas",
            "Registrar mi ciclo",
            "Sorprendeme 💫"
        ])
        def manejar_menu(message):
            opcion = message.text
            if opcion == "Quiero hablar de cómo me siento":
                self.bot.reply_to(message, "¡Hablemos de cómo te sentís! Estoy para escucharte.")
                self.bot.register_next_step_handler(message, self._procesar_sentimiento)

            elif opcion == "Registrar mi ciclo":
                self.bot.reply_to(message, "📅 Escribí la fecha de tu último período (DD/MM/AAAA).")
                self.bot.register_next_step_handler(message, self._procesar_fecha_ciclo)
                fase = self.cycle_tracker.calcular_estado(str(message.chat.id))['fase']

            elif opcion == "Mi cuerpo y mis síntomas":
                estado = self.cycle_tracker.calcular_estado(str(message.chat.id))
                if estado:
                    intro = f"¡Te cuento un poco de cómo va tu ciclo, estás en fase {estado['fase']} 🌼!"
                    if "Menstruación" in estado['fase']:
                        respuesta = "Tu cuerpo está en un proceso de renovación. Date permiso para descansar y cuidarte. 🌙"
                    elif "Fase folicular" in estado['fase']:
                        respuesta = "¡Es momento de nuevos comienzos! Tu energía está en aumento. 🌱"
                    elif "Ovulación" in estado['fase']:
                        respuesta = "¡Estás en tu punto más radiante! Aprovechá esta energía creativa. 🌸"
                    else:  # Fase lútea
                        respuesta = "Es tiempo de reflexión y autocuidado. Escuchá lo que tu cuerpo necesita. 🌕"
                else:
                    intro = "╭🌷━━━━━━━━━━━🌷╮"
                    respuesta = "Te mando una frase motivadora: 'Sos más fuerte de lo que pensás.' 🌷"

                self.bot.reply_to(message, f"{intro}\n\n{self.cycle_tracker.generar_mensaje(str(message.chat.id))}\n\n{respuesta}")
                

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
            pregunta = message.text
            respuesta = self.nlp.buscar_en_dataset(pregunta)
            self.bot.reply_to(message, respuesta or "¡Ups! No encontré una respuesta exacta a tu pregunta en mi base de datos 😥. ¿Hay otra cosa en la que pueda ayudarte?")

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
            fecha = FechaFutura.validar_fecha(message.text.strip())
            self.cycle_tracker.registrar_fecha(chat_id, fecha)
            estado = self.cycle_tracker.calcular_estado(chat_id)
            mensaje = self.cycle_tracker.generar_mensaje(chat_id)
            self.bot.reply_to(message, mensaje)

        except ValueError:
            self.bot.reply_to(message, "⚠️ Formato inválido. Usá DD/MM/AAAA.")
            self.bot.register_next_step_handler(message, self._procesar_fecha_ciclo)
        except FechaFutura:
            self.bot.reply_to(message, "⚠️ La fecha no puede ser futura.")
            self.bot.register_next_step_handler(message, self._procesar_fecha_ciclo)

