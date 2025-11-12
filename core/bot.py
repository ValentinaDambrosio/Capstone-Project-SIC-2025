import telebot
from core.configuracion import Configuracion
from procesadores.procesador_nlp import NLPProcessor
from procesadores.descripcion_imagen import AnalizadorImagen
from procesadores.procesador_audio import AnalizadorAudio
from procesadores.analisis_sentimiento import AnalizadorSentimiento
from ciclo.seguimiento_ciclo import CycleTracker
from core.google_auth import GoogleAuthService
from core.router import Router

class TelegramBotHandler:
    def __init__(self):
        self.token = Configuracion().token_telegram
        self.bot = telebot.TeleBot(self.token)

        # Instancias de módulos
        self.nlp = NLPProcessor("dt_preguntas.json")
        self.imagen_analyzer = AnalizadorImagen()
        self.seguimiento_ciclo = CycleTracker()
        self.audio_analyzer = AnalizadorAudio()
        self.sentiment_analyzer = AnalizadorSentimiento()
        self.google_auth = GoogleAuthService()
        self.router = Router(self.bot, self.nlp, self.imagen_analyzer, self.seguimiento_ciclo, self.audio_analyzer, self.sentiment_analyzer, self.google_auth)

    def iniciar(self):
        print("🤖 Bot inicializado...")
        self.bot.infinity_polling()
    