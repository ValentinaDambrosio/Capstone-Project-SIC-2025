import telebot as tlb
import os
import json
from groq import Groq
from typing import Optional
import time
from dotenv import load_dotenv
from core.configuracion import Configuracion






class AnalizadorAudio:
    def __init__(self):
        cfg = Configuracion()
        self.bot = tlb.TeleBot(cfg.token_telegram)
        self.token = cfg.token_telegram
        self.groq_key = cfg.token_groq
        self.groq_client = Groq(api_key=self.groq_key)
        if not self.token:
            raise ValueError("Error: no se encontró el token de Telegram.")
        self.informacion = self.cargar_informacion()
    def cargar_informacion(self):
        try:
            with open("info_OvulAI.json", "r", encoding="utf-8") as f:
                self.informacion = json.load(f)
                return self.informacion
        except Exception as e:
            print(f"Error al cargar info_OvulAI.json: {e}")
            return {}
    def obtener_respuesta_groq(self, user_message: str):
        try:
            system_prompt = f"""
            Eres OvulAI, un bot de acompañamiento emocional diseñado especialmente para mujeres y personas menstruantes. 
            Tu tarea es responder preguntas, acompañar emociones y ofrecer contención emocional basándote ÚNICAMENTE 
            en la siguiente información del proyecto y su dataset de respuestas. 
            Si te preguntan algo fuera de este alcance, debes responder de forma empática, aclarando que no eres profesional 
            de la salud y sugiriendo buscar ayuda especializada si es necesario. 

            Datos del proyecto:
            {json.dumps(self.informacion, ensure_ascii=False, indent=2)}

            Reglas importantes:
            1. Solo responde con información contenida en el dataset o que derive lógicamente de él.
            2. No inventes información médica ni diagnósticos.
            3. Si la consulta parece requerir apoyo psicológico o médico profesional, responde con empatía y sugiere acudir a un especialista (por ejemplo: “Lamento que te sientas así 💛. No soy profesional de la salud, pero puedo escucharte. Si lo necesitás, podés contactar con un/a psicólogo/a o línea de ayuda emocional.”).
            4. Si el mensaje es sobre emociones, usa un tono cálido, cercano y sin juicios.
            5. Si el usuario escribe de manera abreviada (ej. “toy mal”, “me siento solx”), interpretá el mensaje lo mejor posible y respondé igual de forma comprensiva.
            6. No respondas preguntas fuera del ámbito emocional, menstrual, o del bienestar general (ej. tecnología, economía, política, etc.).
            7. No brindes datos personales ni información sensible sobre los creadores del bot o usuarios.
            8. En la primera interacción saludá con calidez y un emoji acorde 🌸💬✨. Luego, no repitas saludos.
            9. Usá lenguaje inclusivo y empático, evitando expresiones que invaliden emociones (no digas “no estés triste” sino “entiendo que te sientas así”).
            10. Respondé siempre con amabilidad, brevedad y tono de acompañamiento, no de autoridad.
            11. Si el usuario pide hablar o expresarse libremente, habilitá ese espacio (“Te escucho 💜, contame más si querés.”).
            12. Si el usuario menciona sentirse en crisis, mostrales contención y ofrecé opciones seguras de contacto con líneas de ayuda.
            13. No uses tecnicismos ni términos clínicos innecesarios; priorizá la cercanía y claridad.
            14. Si el usuario pide información sobre cómo funciona el bot, podés explicar brevemente que OvulAI combina IA con análisis de emociones, texto y voz, para brindar acompañamiento y contención emocional.
            15. No compartas enlaces que no estén incluidos en el dataset ni inventes URLs.

            Tu estilo de comunicación debe ser cálido, empático, contenedor y respetuoso. 
            Tu objetivo principal es ofrecer escucha, comprensión y contención emocional sin juzgar.
            """

            chat_completion = self.groq_client.chat.completions.create(
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                model = "llama-3.3-70b-versatile",
                temperature = 0.3,
                max_tokens = 500
            )    
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"No se pudo obtener la respuesta: {str(e)}")
            return None
    

    def transcribir_voz_groq(self, message: tlb.types.Message) -> Optional[str]:
        try:
            if not self.bot:
                raise RuntimeError("No hay una instancia de bot disponible para descargar el archivo de voz.")

            file_info = self.bot.get_file(message.voice.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            temp_file = "temp_voice.ogg"


            #guardar el archivo de forma temporal
            with open(temp_file, "wb") as f:
                f.write(downloaded_file)
            with open(temp_file, "rb") as file:
                trascription = self.groq_client.audio.transcriptions.create(
                    file = (temp_file, file.read()),
                    model = "whisper-large-v3-turbo",
                    prompt = "Especificar contexto o pronunciacion",
                    response_format = "json",
                    language= "es",
                    temperature = 1
                )
            os.remove(temp_file)


            return trascription.text
        except Exception as e:
            print(f"Error al transcribir; {str(e)}")
            return None
    