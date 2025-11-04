from telebot import types
from datetime import datetime


class Router:
    def __init__(self, bot, nlp, imagen_analyzer, cycle_tracker, audio_analyzer):
        self.bot = bot
        self.nlp = nlp
        self.imagen_analyzer = imagen_analyzer
        self.audio_analyzer = audio_analyzer
        self.cycle_tracker = cycle_tracker
        self._registrar_rutas()

    def _registrar_rutas(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def menu(message):
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
            for b in botones:
                teclado.add(types.KeyboardButton(b))
            self.bot.send_message(message.chat.id, "🌸 *MENÚ PRINCIPAL*", parse_mode="Markdown", reply_markup=teclado)
        
        @self.bot.message_handler(func=lambda message: message.text in [
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
                self.bot.reply_to(message, "💬 Contame, ¿cómo te sentís hoy?")
            elif opcion == "2️⃣ Catarsis time":
                self.bot.reply_to(message, "😮‍💨 Este es tu espacio de catarsis. Podés desahogarte libremente.")
            elif opcion == "3️⃣ Necesito relajarme":
                self.bot.reply_to(message, "🧘 Acá van algunas ideas para relajarte: respiración, música tranquila, o escribir lo que sentís.")
            elif opcion == "4️⃣ Ciclo y emociones":
                self.bot.reply_to(message, "🌕 Tu ciclo puede influir en cómo te sentís. Probá usar /ciclo para registrarlo o ver en qué fase estás.")
            elif opcion == "5️⃣ Mi cuerpo y mis síntomas":
                self.bot.reply_to(message, "💡 Contame qué síntomas estás notando para ayudarte a entenderlos mejor.")
            elif opcion == "6️⃣ Tips de autocuidado":
                self.bot.reply_to(message, "💅 Algunos tips de autocuidado: dormí bien, comé algo rico, movete un poco y tomate tu tiempo 💕.")
            elif opcion == "7️⃣ Registrar mi día":
                self.bot.reply_to(message, "📓 Escribí cómo fue tu día para guardarlo en tu registro personal.")
            elif opcion == "8️⃣ Sorprendeme 💫":
                self.bot.reply_to(message, "✨ Te mando una frase motivadora: *'Sos más fuerte de lo que pensás.'* 🌷")

        @self.bot.message_handler(commands=['ciclo'])
        def ciclo(message):
            chat_id = str(message.chat.id)
            estado = self.cycle_tracker.calcular_estado(chat_id)
            if estado:
                msg = (
                    f"🩷 Último período: {estado['ultimo']}\n"
                    f"⏱️ Día del ciclo: {estado['dia_ciclo']}\n"
                    f"💫 Fase actual: {estado['fase']}\n"
                    f"📅 Próximo período estimado: {estado['proximo']} ({estado['restantes']} días restantes)"
                )
                self.bot.reply_to(message, msg)
            else:
                self.bot.reply_to(message, "🩸 Escribí la fecha de tu último período (DD/MM/AAAA).")
                self.bot.register_next_step_handler(message, self._guardar_fecha)
        
        def _guardar_fecha(message):
            chat_id = str(message.chat.id)
            try:
                fecha = datetime.strptime(message.text.strip(), "%d/%m/%Y")
                self.cycle_tracker.registrar_fecha(chat_id, fecha)
                estado = self.cycle_tracker.calcular_estado(chat_id)
                msg = (
                    f"✅ Fecha registrada: {estado['ultimo']}\n"
                    f"💫 Fase actual: {estado['fase']}\n"
                    f"📅 Próximo período estimado: {estado['proximo']} ({estado['restantes']} días restantes)"
                )
                self.bot.reply_to(message, msg)
            except ValueError:
                self.bot.reply_to(message, "⚠️ Formato inválido. Usá DD/MM/AAAA.")
                self.bot.register_next_step_handler(message, self._guardar_fecha)
        
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

        @self.bot.message_handler(func=lambda msg:True)
        def responder(message):
            pregunta = message.text
            respuesta = self.nlp.buscar_en_dataset(pregunta)
            self.bot.reply_to(message, respuesta or "No encontré una respuesta exacta.")