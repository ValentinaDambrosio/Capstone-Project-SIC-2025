import base64
import requests
import os

class AnalizadorImagen:
    def __init__(self):
        self.groq_apikey = os.getenv('GROQ_TOKEN')
        self.groq_url = os.getenv('GROQ_URL')
    
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
        headers = {"Authorization": f"Bearer {self.groq_apikey}", "Content-Type": "application/json"}
        data = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "Por favor describe esta imagen en español."
                        "Incluye colores, objetos y relación con el ciclo menstrual si aplica."
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