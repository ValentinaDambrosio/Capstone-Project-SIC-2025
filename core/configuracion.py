import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_TOKEN")
GROQ_URL = os.getenv("GROQ_URL")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/calendar.events")


class Configuracion:
    def __init__(self):
        self.token_groq = GROQ_API_KEY
        self.token_telegram = TELEGRAM_TOKEN
        self.groq_url = GROQ_URL
        self.client_id = GOOGLE_CLIENT_ID
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.redirect_uri = GOOGLE_REDIRECT_URI
        self.scopes = GOOGLE_SCOPES
        if not TELEGRAM_TOKEN or not GROQ_API_KEY or not GROQ_URL or not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI or not GOOGLE_SCOPES:
            raise ValueError("Error: faltan variables en el archivo .env")
