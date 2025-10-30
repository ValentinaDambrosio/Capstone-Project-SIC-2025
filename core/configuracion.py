import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_TOKEN")
GROQ_URL = os.getenv("GROQ_URL")
class Configuracion:
    def __init__(self):
        self.token_groq = GROQ_API_KEY
        self.token_telegram = TELEGRAM_TOKEN
        self.groq_url = GROQ_URL
        if not TELEGRAM_TOKEN or not GROQ_API_KEY:
            raise ValueError("Error: faltan variables en el archivo .env")
