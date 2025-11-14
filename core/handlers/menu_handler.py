from telebot import types


class MenuHandler:
    def __init__(self, router):
        self.router = router
        self.bot = router.bot
    
    def iniciar(self, message):
        chat_id = message.chat.id
        self.bot.send_message(chat_id, "Hola, soy OvulAI, tu bot de confianza. Estoy acá para acompañarte y escucharte 💕Contame, ¿qué necesitás hoy?")
        self.mostrar_menu(chat_id)

    def mostrar_menu(self, chat_id):
        teclado = types.InlineKeyboardMarkup(row_width=1)
        botones = [
            types.InlineKeyboardButton("Quiero hablar de cómo me siento 💬", callback_data="sentimientos"),
            types.InlineKeyboardButton("Mi cuerpo y mis síntomas 🧘‍♀️", callback_data="sintomas"),
            types.InlineKeyboardButton("Registrar mi ciclo 📅", callback_data="ciclo"),
            types.InlineKeyboardButton("Conectar mi calendario 🔗", callback_data="google_auth"),
            types.InlineKeyboardButton("Sorprendeme 💫", callback_data="sorpresa"),
            types.InlineKeyboardButton("Información OvulAI ℹ️", callback_data="info")
  
        ]
        teclado.add(*botones)

        self.bot.send_message(
            chat_id,
            "🌸 *MENÚ PRINCIPAL*\n¡Elige una opción o comienza a chatear conmigo!",
            parse_mode="Markdown",
            reply_markup=teclado
        )
    
    def boton_volver(self, mensaje):
        chat_id = mensaje.chat.id
        teclado = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        boton_volver = types.KeyboardButton("🔙 Volver al menú")
        teclado.add(boton_volver)
        self.bot.send_message(
            chat_id,
            "Volviendo al menú principal...",
            reply_markup=teclado)
        self.router.modos[chat_id] = "menu"
        self.mostrar_menu(chat_id)
    
    def manejar_boton(self, call):
        data = call.data
        chat_id = call.message.chat.id

        r = self.router

        if data == "sentimientos":
            r.modos[chat_id] = "sentimientos"
            r.sentimientos.iniciar(call)

        elif data == "ciclo":
            r.modos[chat_id] = "ciclo"
            r.ciclo.iniciar(call)

        elif data == "sintomas":
            r.modos[chat_id] = "sintomas"
            r.sintomas.mostrar_sintomas(call.message)
            

        elif data == "google_auth":
            r.google.iniciar(call)

        elif data == "sorpresa":
            r.modos[chat_id] = "menu"
            r.sorpresa.iniciar(call)

        elif data == "info":
            self.enviar_info(chat_id)
    
    def enviar_info(self, chat_id):
        info_texto = (
                        "🌸 *Información sobre OvulAI* 🌸\n\n"
                        "¡Hola! Soy *OvulAI*, tu asistente de confianza 💕. Estoy aquí para acompañarte en temas de emociones, autocuidado y seguimiento de tu ciclo menstrual.\n\n"
                        "Conmigo podés:\n"
                        "💬 Hablar de cómo te sentís y recibir consejos emocionales.\n"
                        "📅 Registrar tu ciclo menstrual y obtener recomendaciones personalizadas según tu fase.\n"
                        "🧘‍♀️ Consultar sobre tu cuerpo y tus síntomas.\n"
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
        self.router.modos[chat_id] = "menu"
        self.router.menu.mostrar_menu(chat_id)