from core.configuracion import Configuracion
from transformers import pipeline
import os


class AnalizadorSentimiento:

    def __init__(self):
        cfg = Configuracion()
        self.groq_apikey = cfg.token_groq
        self.groq_url = cfg.groq_url
        self.analizador_sentimientos = pipeline("sentiment-analysis", 
        model = "pysentimiento/robertuito-sentiment-analysis")

    def analizar_sentimiento(self, frase):
        resultado = self.analizador_sentimientos(frase)[0]
        sentimiento = resultado['label']
        confianza = resultado['score']
        if sentimiento == 'POS':
            if confianza > 0.75:
                respuesta_sentimiento = "Veo que te sientes muy bien 😊. ¡Me alegra mucho!"
            else:
                respuesta_sentimiento = "Parece que te sentís bien 🙂. ¡Qué bueno!"
        elif sentimiento == 'NEU':
            respuesta_sentimiento = "Parece que tu reacción es bastante neutral. Estoy aquí si querés compartir más."
        elif sentimiento == 'NEG':
            if confianza > 0.75:
                respuesta_sentimiento = "Lamento que te sientas así 💛. No soy profesional de la salud, pero puedo escucharte. Si lo necesitás, podés contactar con un/a psicólogo/a o línea de ayuda emocional."
            else:
                respuesta_sentimiento = "Parece que no te sentís del todo bien 😕. Estoy aquí para escucharte si querés contarme más."
        else:
            respuesta_sentimiento = f"No pude determinar cómo te sentís, mi sistema arroja un nivel de confianza del {resultado['score']:.2f} Pero estoy aquí para escucharte."
        return respuesta_sentimiento