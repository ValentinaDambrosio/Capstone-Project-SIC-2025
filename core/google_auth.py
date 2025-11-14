import os
import json
import requests
from urllib.parse import urlencode
from core.configuracion import Configuracion


class TokenStorage:
    """Storage simple en JSON; podés reemplazar por DB."""
    def __init__(self, path="google_tokens.json"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def guardar(self, user_id: str, token_data: dict):
        with open(self.path, "r", encoding="utf-8") as f:
            all_tokens = json.load(f)
        all_tokens[str(user_id)] = token_data
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(all_tokens, f, indent=2)

    def obtener(self, user_id: str):
        with open(self.path, "r", encoding="utf-8") as f:
            all_tokens = json.load(f)
        return all_tokens.get(str(user_id))

    def borrar(self, user_id: str):
        with open(self.path, "r", encoding="utf-8") as f:
            all_tokens = json.load(f)
        if str(user_id) in all_tokens:
            del all_tokens[str(user_id)]
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(all_tokens, f, indent=2)
            return True
        return False

class GoogleAuthService:
    def __init__(self):
        self.client_id = Configuracion().client_id
        self.client_secret = Configuracion().client_secret
        self.redirect_uri = Configuracion().redirect_uri
        self.scopes = Configuracion().scopes
        self.token_storage = TokenStorage()

    def generar_link_autorizacion(self, chat_id: str):
        base = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scopes,
            "access_type": "offline",   # Importante para refresh_token
            "prompt": "consent",       # Forzar refresh_token la 1ra vez
            "state": str(chat_id)
        }
        return f"{base}?{urlencode(params)}"

    def intercambiar_code_por_tokens(self, code: str):
        url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        r = requests.post(url, data=data)
        r.raise_for_status()
        return r.json()   # Contiene access_token, refresh_token, expires_in, id_token

    # Helper para que el endpoint use:
    def guardar_tokens_para_usuario(self, chat_id: str, token_data: dict):
        self.token_storage.guardar(chat_id, token_data)

    def obtener_tokens(self, chat_id: str):
        return self.token_storage.obtener(chat_id)

    def borrar_tokens(self, chat_id: str):
        return self.token_storage.borrar(chat_id)
