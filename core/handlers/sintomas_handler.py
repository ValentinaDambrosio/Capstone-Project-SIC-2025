from telebot import types
from procesadores.procesador_nlp import MenstrualNLPProcessor


class SintomasHandler:
    def __init__(self, router):
        self.router = router
        self.bot = router.bot
        self.cycle = router.cycle_tracker

    def _boton_volver(self, chat_id, mensaje):
        teclado = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        boton_volver = types.KeyboardButton("🔙 Volver al menú")
        teclado.add(boton_volver)
        self.bot.send_message(chat_id, mensaje, reply_markup=teclado)
    
    def mostrar_sintomas(self, message):
        chat_id = message.chat.id
        self.router.modos[chat_id] = "sintomas"
        estado = self.cycle.calcular_estado(str(chat_id))
        
        if estado:
            intro = f"¡Te cuento cómo va tu ciclo, estás en fase '{estado['fase']}' 🌼!"
            mensaje = self.cycle.generar_mensaje(str(chat_id))

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
            self._boton_volver(chat_id, mensaje_final)
            self.bot.register_next_step_handler(message, self._dar_recomendaciones_fase)
        else:
            intro = "╭🌷━━━━━━━━━━━🌷╮"
            mensaje = "Todavía no registraste tu última fecha de ciclo 🌸\nPodés hacerlo con el botón 'Registrar mi ciclo' 📅"
            respuesta = "Te mando una frase motivadora: 'Sos más fuerte de lo que pensás.' 🌷"
            self._boton_volver(chat_id, mensaje_final)
            return
        
    def _dar_recomendaciones_fase(self, message):
        chat_id = message.chat.id
        self.router.modos[chat_id] = "sintomas"
        estado = self.cycle.calcular_estado(str(chat_id))

        if message.text is None:
            self.bot.reply_to(
                            message,
                            "Vi que enviaste algo que no es texto 💬. Por ahora solo puedo responder a consultas escritas sobre tu ciclo y síntomas. 🌸"
                            )
            self.bot.register_next_step_handler(message, self._dar_recomendaciones_fase)
            return
        
        if message.text.lower() in ["volver al menú", "🔙 volver al menú"]:
            self.router.modos[chat_id] = "menu"
            markup_vacio = types.ReplyKeyboardRemove()
            self.bot.send_message(chat_id, "🔙 Volviendo al menú principal...", reply_markup=markup_vacio)
            self.router.menu.mostrar_menu(chat_id)
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