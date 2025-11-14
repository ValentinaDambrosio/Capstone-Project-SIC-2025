# core/google_calendar.py
import os
import time
import requests
from datetime import datetime, date, timedelta
from typing import Optional


class GoogleCalendarClient:
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    EVENT_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    def __init__(self, token_storage):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.token_storage = token_storage  # instancia de TokenStorage de google_auth

    def _refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        """Pide un nuevo access_token usando refresh_token. Devuelve dict con access_token + expires_in."""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        r = requests.post(self.TOKEN_URL, data=payload)
        if r.status_code != 200:
            print(f"⚠️ Error refrescando token: {r.status_code} {r.text}")
            return None
        return r.json()

    def _obtener_access_token_para_usuario(self, chat_id: str) -> Optional[str]:
        tokens = self.token_storage.obtener(chat_id)
        if not tokens:
            return None

        # tokens guardados pueden no incluir expires_at; manejamos por expires_in y/o id_token
        access_token = tokens.get("access_token")
        expires_at = tokens.get("expires_at")  # si lo guardaste al intercambiar
        refresh_token = tokens.get("refresh_token")

        # Si no hay expiration info, asumimos que precisa refresh si access_token no existe
        if access_token and expires_at:
            if time.time() < expires_at:
                return access_token

        # si llegamos acá, intentamos refrescar
        if refresh_token:
            new = self._refresh_access_token(refresh_token)
            if not new:
                return None
            # actualizar storage: merge values y guarda expires_at
            tokens.update(new)
            if "expires_in" in new:
                tokens["expires_at"] = time.time() + int(new.get("expires_in", 0))
            # si refresh_token no viene en respuesta, preservalo (Google raramente lo envía en refresh)
            if "refresh_token" not in new and refresh_token:
                tokens["refresh_token"] = refresh_token
            self.token_storage.guardar(chat_id, tokens)
            return tokens.get("access_token")
        return None

    def crear_evento(self, chat_id: str, fecha_inicio: datetime, titulo: str, descripcion: str = "", all_day: bool = False, color_id: Optional[str] = None):
        # Obtener tokens directamente desde el token_storage
        tokens = self.token_storage.obtener(chat_id)
        if not tokens:
            print(f"⚠️ No hay tokens guardados para el usuario {chat_id}.")
            return False

        access_token = tokens.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        evento = {
            "summary": titulo,
            "description": descripcion,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 3 * 24 * 60}  # 3 días antes
                ]
            }
        }

        # Construir start/end dependiendo si es all-day o con hora
        if all_day:
            # aceptar date o datetime
            if isinstance(fecha_inicio, datetime):
                start_date = fecha_inicio.date()
            else:
                start_date = fecha_inicio
            # Google espera end = fecha siguiente (exclusivo) para all-day events
            evento["start"] = {"date": start_date.isoformat()}
            evento["end"] = {"date": (start_date + timedelta(days=1)).isoformat()}
        else:
            evento["start"] = {"dateTime": fecha_inicio.isoformat(), "timeZone": "America/Argentina/Buenos_Aires"}
            evento["end"] = {"dateTime": (fecha_inicio + timedelta(hours=1)).isoformat(), "timeZone": "America/Argentina/Buenos_Aires"}

        if color_id is not None:
            # Asegurar que sea string (Google acepta ids como strings '1'..'11')
            evento["colorId"] = str(color_id)

        response = requests.post(self.EVENT_URL, headers=headers, json=evento)

        if response.status_code == 401:  # Token expirado → intentar refrescar usando refresh_token
            print("🔄 Token expirado, intentando refrescar...")
            # intentar refrescar a través del flujo interno
            nuevo_access = self._obtener_access_token_para_usuario(chat_id)
            if nuevo_access:
                headers["Authorization"] = f"Bearer {nuevo_access}"
                response = requests.post(self.EVENT_URL, headers=headers, json=evento)
                if response.status_code in (200, 201):
                    print("✅ Evento creado correctamente en Google Calendar (tras refresh).")
                    return True
                else:
                    print(f"⚠️ Error al crear el evento tras refresh: {response.status_code} {response.text}")
                    return False
            else:
                print("❌ No se pudo refrescar el token.")
                return False

        if response.status_code not in (200, 201):
            print(f"⚠️ Error al crear el evento: {response.status_code}")
            return False

        print("✅ Evento creado correctamente en Google Calendar.")
        return True

    def crear_eventos_ciclo(self, chat_id: str, fecha_ultimo_ciclo: datetime):
        """Crea el evento del último y del próximo ciclo."""
        # Aceptar tanto date como datetime; si es date, convertir a datetime a las 09:00
        if isinstance(fecha_ultimo_ciclo, date) and not isinstance(fecha_ultimo_ciclo, datetime):
            fecha_ultimo_dt = datetime.combine(fecha_ultimo_ciclo, datetime.min.time()).replace(hour=9, minute=0)
        else:
            # si ya es datetime, forzamos la hora a las 09:00
            fecha_ultimo_dt = fecha_ultimo_ciclo.replace(hour=9, minute=0)

        proximo_ciclo = fecha_ultimo_dt + timedelta(days=28)

        # Evento del último ciclo
        self.crear_evento(
            chat_id,
            fecha_ultimo_dt,
            titulo="🌸 Inicio de mi último ciclo menstrual",
            descripcion="Registro del último ciclo en OvulAI",
            all_day=True,
            color_id="11"
        )

        # Evento del próximo ciclo estimado
        self.crear_evento(
            chat_id,
            proximo_ciclo,
            titulo="🩸 Inicio estimado de mi próximo ciclo",
            descripcion="Estimación automática del próximo ciclo.",
            all_day=True,
            color_id="9"
        )

        return proximo_ciclo
