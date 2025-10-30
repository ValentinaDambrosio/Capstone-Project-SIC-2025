import os
import telebot
from procesadores.procesador_nlp import NLPProcessor
from procesadores.descripcion_imagen import AnalizadorImagen
from ciclo.seguimiento_ciclo import CycleTracker
from core.router import Router

class TelegramBotHandler:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        if not self.token:
            raise ValueError("❌ No se encontró TELEGRAM_TOKEN en el archivo .env")
        self.bot = telebot.TeleBot(self.token)

        # Instancias de módulos
        self.nlp = NLPProcessor("dataset.json")
        self.imagen_analyzer = AnalizadorImagen()
        self.seguimiento_ciclo = CycleTracker()

        self.router = Router(self.bot, self.nlp, self.imagen_analyzer, self.seguimiento_ciclo)

    def iniciar(self):
        print("🤖 Bot inicializado...")
        self.bot.infinity_polling()
    