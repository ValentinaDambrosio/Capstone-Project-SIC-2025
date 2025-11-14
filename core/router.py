from telebot import types
from core.handlers.menu_handler import MenuHandler
from core.handlers.sentimientos_handler import SentimientosHandler
from core.handlers.ciclo_handler import CicloHandler
from core.handlers.sintomas_handler import SintomasHandler
from core.handlers.google_handler import GoogleAuthHandler
from core.google_calendario import GoogleCalendarClient
from core.handlers.sorpresa_handler import SorpresaHandler
from core.handlers.multimedia_handler import MultimediaHandler


class Router:
    def __init__(self, bot, nlp, imagen_analyzer, cycle_tracker, audio_analyzer, sentiment_analyzer, google_auth):
        self.bot = bot
        self.nlp = nlp
        self.imagen_analyzer = imagen_analyzer
        self.cycle_tracker = cycle_tracker
        self.audio_analyzer = audio_analyzer
        self.sentiment_analyzer = sentiment_analyzer
        self.google_auth = google_auth
        self.google_calendar = GoogleCalendarClient(self.google_auth.token_storage)

        self.modos = {}

        # Handlers
        self.menu = MenuHandler(self)
        self.sentimientos = SentimientosHandler(self)
        self.ciclo = CicloHandler(self)
        self.sintomas = SintomasHandler(self)
        self.google = GoogleAuthHandler(self)
        self.sorpresa = SorpresaHandler(self)
        self.multimedia = MultimediaHandler(self)

        self._registrar_rutas()

    # ============================
    # REGISTRO DE RUTAS
    # ============================
    def _registrar_rutas(self):

        # START
        @self.bot.message_handler(commands=['start', 'help'])
        def start(message):
            self.modos[message.chat.id] = "menu"
            self.menu.iniciar(message)

        # BOTÓN VOLVER
        @self.bot.message_handler(func=lambda m: m.text in ["volver al menú", "🔙 Volver al menú"])
        def volver(message):
            self.menu.boton_volver(message)

        # BOTONES DEL MENÚ
        @self.bot.callback_query_handler(func=lambda call: True)
        def botones(call):
            self.menu.manejar_boton(call)

        # IMÁGENES
        @self.bot.message_handler(content_types=['photo'])
        def imagen(message):
            self.multimedia.procesar_imagen(message)

        # AUDIO
        @self.bot.message_handler(content_types=['voice'])
        def audio(message):
            self.multimedia.manejar_audio(message)

        # MENSAJE LIBRE
        @self.bot.message_handler(func=lambda msg: True)
        def texto(message):
            chat_id = message.chat.id
            modo = self.modos.get(chat_id, "menu")

            if modo == "sentimientos":
                self.sentimientos.procesar(message)
            elif modo == "ciclo":
                self.ciclo.procesar_fecha_ciclo(message)
            elif modo == "menu":
                respuesta = self.nlp.buscar_en_dataset(message.text, umbral = 0.7)
                self.bot.reply_to(message, respuesta or "No encontré una respuesta exacta en mi base de datos. Por favor, probá con otra pregunta.")
            else:
                self.menu.mostrar_menu(chat_id)
        