import requests
from deep_translator import GoogleTranslator as Translator


class FraseInspiradora():
    def __init__(self):
        pass

    def obtener_frase_inspiradora(self):
        url = "https://zenquotes.io/api/random"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()[0]
                frase_en = data["q"]
                frase_es = Translator(source='en', target='es').translate(frase_en)
                autor = data["a"]
                return f"🪷 *Frase del día:* “{frase_es}”\n— {autor}"
            else:
                return "No pude conseguir una frase por ahora 😕."
        except Exception as e:
            return f"Error al obtener frase: {e}"