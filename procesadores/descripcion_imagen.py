import base64
import requests
import os
from core.configuracion import Configuracion


class AnalizadorImagen:
    def __init__(self):
        cfg = Configuracion()
        self.token = cfg.token_telegram
        self.groq_key = cfg.token_groq
        self.groq_url = cfg.groq_url
    
    def imagen_a_base64(self, ruta_o_bytes_imagen):
        try:
            if isinstance(ruta_o_bytes_imagen, bytes):
                return base64.b64encode(ruta_o_bytes_imagen).decode('utf-8')
            else:
                with open(ruta_o_bytes_imagen, "rb") as f:
                    return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error al convertir imagen: {e}")
            return None
        
    def describir_imagen(self, imagen_base64):
        headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
        data = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                    {
                    "role": "system",
                    "content": (
                        "Eres un asistente de acompañamiento emocional enfocado en la salud y el ciclo menstrual. "
                        "Proporciona apoyo, información sobre autocuidado y prevención de ETS o embarazo si aplica, "
                        "de manera clara y empática."
                    )
                    },
                    {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            
                            "Cuando describas una imagen, haz lo siguiente:"
                            "1. Todas las descripciones que hagas deben estar claras y en español"
                            "2. Relaciona la imagen con el bienestar, autocuidado o estados de ánimo."
                            "3. Si es apropiado, incluye información educativa sobre prevención de ETS, embarazo o salud sexual de manera clara y responsable."
                            "4. Siempre comunica con empatía y respeto, evitando alarmar al usuario."
                            "5. Si la imagen no tiene relación con el bienestar o la salud menstrual, indícalo amablemente."
                            "6. Si das consejos sobre salud, recuerda que no eres un profesional médico y sugiere consultar a un especialista si es necesario."
                            "7. No hagas preguntas como ¿Quieres que te cuente más?; solo proporciona una descripción y consejos si aplica."

                        )},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}}
                                ]
                            }]
                    }
        try:
            resp = requests.post(self.groq_url, headers=headers, json=data, timeout=40)
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content']
            else:
                return f"Error Groq Imagen: {resp.status_code}"
        except Exception as e:
            return f"Error al describir imagen: {e}"