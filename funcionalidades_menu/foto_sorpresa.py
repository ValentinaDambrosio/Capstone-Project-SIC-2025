import requests


class FotoSorpresa():
    def __init__(self):
        pass

    def obtener_foto_random(self):
        try:
            while True:
                resp = requests.get("https://random.dog/woof.json")
                data = resp.json()
                imagen = data.get("url")
                if imagen.endswith((".jpg", ".jpeg", ".png", ".gif", ".mp4", ".webm")):
                        break
            return imagen
        except Exception:
                return None