from telebot import types
from procesadores.procesador_nlp import NLPProcessor


class SentimientosHandler:
    def __init__(self, router):
        self.router = router
        self.bot = router.bot
        self.sentiment_analyzer = router.sentiment_analyzer

    def _boton_volver(self, chat_id):
        teclado = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        boton_volver = types.KeyboardButton("🔙 Volver al menú")
        teclado.add(boton_volver)
        return teclado
    
    def iniciar(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(
            chat_id,
            "💕¡Hablemos de cómo te sentís! Estoy para escucharte.",
            parse_mode="Markdown",
            reply_markup=self._boton_volver(chat_id)
        )
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.procesar)
    
    def procesar(self, message):
        chat_id = message.chat.id
        try:
            if message.text is None:
                self.bot.reply_to(
                    message,
                    "Vi que enviaste algo que no es texto 💬. Por ahora solo puedo responder a mensajes escritos sobre cómo te sentís. 🌷"
                )
                self.bot.register_next_step_handler_by_chat_id(chat_id, self.procesar)
                return
            
            if message.text.lower() in ["volver al menú", "🔙 volver al menú"]:
                self.router.modos[chat_id] = "menu"
                markup_vacio = types.ReplyKeyboardRemove()
                self.bot.send_message(chat_id, "🔙 Volviendo al menú principal...", reply_markup=markup_vacio)
                self.router.menu.mostrar_menu(chat_id)
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
            self.bot.register_next_step_handler_by_chat_id(chat_id, self.procesar)
    
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