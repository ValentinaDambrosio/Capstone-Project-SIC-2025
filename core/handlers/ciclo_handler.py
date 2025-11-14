from telebot import types
from excepciones.excepciones_fechas import ExceptionFechas


class CicloHandler:
    def __init__(self, router):
        self.router = router
        self.bot = router.bot
        self.cycle = router.cycle_tracker
        self.google = router.google_auth
        self.calendar = router.google_calendar
    
    def _boton_volver(self, chat_id):
        teclado = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        boton_volver = types.KeyboardButton("🔙 Volver al menú")
        teclado.add(boton_volver)
        return teclado
    
    def iniciar(self, call):
        chat_id = call.message.chat.id
        self.bot.send_message(
            chat_id,
            "📅 Escribí la fecha de tu último período (DD/MM/AAAA).",
            parse_mode="Markdown",
            reply_markup=self._boton_volver(chat_id)
        )
        self.bot.register_next_step_handler_by_chat_id(call.message, self.procesar_fecha_ciclo)
    
    def procesar_fecha_ciclo(self, message):
        chat_id = message.chat.id
        try:
            fecha = ExceptionFechas.validar_fecha(message.text.strip())
            self.cycle.registrar_fecha(chat_id, fecha)

            estado = self.cycle.calcular_estado(chat_id)
            self.bot.reply_to(message, f"¡Fecha registrada! Estás en la fase: '{estado['fase']}'. Para más info, por favor volvé al menú y seleccioná 'Mi cuerpo y mis síntomas' 🌼🩷.")
            
            if not self.google.obtener_tokens(chat_id):
                self.bot.send_message(
                    chat_id,
                    "⚠️ Aún no conectaste tu cuenta de Google Calendar. "
                    "Podés hacerlo desde el menú principal con el botón 'Conectar con Google' 🔗"
                )
            else:
                proximo = self.router.google_calendar.crear_eventos_ciclo(chat_id, fecha)
                
            self.router.modos[int(chat_id)] = "menu"
            self.router.menu.mostrar_menu(int(chat_id))

        except ValueError:
            self.bot.reply_to(message, "⚠️ Formato inválido. Usá DD/MM/AAAA.")
            self.bot.register_next_step_handler(message, self.procesar_fecha_ciclo)
        except ExceptionFechas as e:
            self.bot.reply_to(message, f"⚠️{e}")
            self.bot.register_next_step_handler(message, self.procesar_fecha_ciclo)