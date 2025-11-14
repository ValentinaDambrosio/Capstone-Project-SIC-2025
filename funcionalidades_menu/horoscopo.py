from datetime import datetime
from deep_translator import GoogleTranslator as Translator
import requests


class Horoscopo():
    def __init__(self, bot, router):
        self.bot = bot 
        self.router = router
    
    def obtener_signo(self, message):
        chat_id = message.chat.id
        self.bot.send_message(
            chat_id,
            "✨ Por favor, ingresá tu fecha de nacimiento en formato *DD/MM* o *DD/MM/AAAA* para saber tu signo zodiacal."
        )
        self.bot.register_next_step_handler(message, self._procesar_signo_zodiacal)

    def _procesar_signo_zodiacal(self, message):
        chat_id = message.chat.id
        fecha_str = message.text.strip()

        try:
            partes = fecha_str.split("/")
            if len(partes) == 2:
                fecha = datetime.strptime(fecha_str, "%d/%m")
            else:
                fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            self.bot.send_message(chat_id, f"⚠️ Escribí algo como *23/08* o *23/08/1998*.")
            self.bot.register_next_step_handler(message, self._procesar_signo_zodiacal)
            return

        dia, mes = fecha.day, fecha.month

        if (mes == 12 and dia >= 22) or (mes == 1 and dia <= 19):
            signo = "capricorn"
            español = "Capricornio"
        elif (mes == 1 and dia >= 20) or (mes == 2 and dia <= 18):
            signo = "aquarius"
            español = "Acuario"
        elif (mes == 2 and dia >= 19) or (mes == 3 and dia <= 20):
            signo = "pisces"
            español = "Piscis"
        elif (mes == 3 and dia >= 21) or (mes == 4 and dia <= 19):
            signo = "aries"
            español = "Aries"
        elif (mes == 4 and dia >= 20) or (mes == 5 and dia <= 20):
            signo = "taurus"
            español = "Tauro"
        elif (mes == 5 and dia >= 21) or (mes == 6 and dia <= 20):
            signo = "gemini"
            español = "Géminis"
        elif (mes == 6 and dia >= 21) or (mes == 7 and dia <= 22):
            signo = "cancer"
            español = "Cáncer"
        elif (mes == 7 and dia >= 23) or (mes == 8 and dia <= 22):
            signo = "leo"
            español = "Leo"
        elif (mes == 8 and dia >= 23) or (mes == 9 and dia <= 22):
            signo = "virgo"
            español = "Virgo"
        elif (mes == 9 and dia >= 23) or (mes == 10 and dia <= 22):
            signo = "libra"
            español = "Libra"
        elif (mes == 10 and dia >= 23) or (mes == 11 and dia <= 21):
            signo = "scorpio"
            español = "Escorpio"
        else:
            signo = "sagittarius"
            español = "Sagitario"

        self.bot.send_message(chat_id, f"🌟 Tu signo solar zodiacal es *{español}* 🌟")
        self.obtener_horoscopo(chat_id, signo)

    def obtener_horoscopo(self, chat_id, signo):
        url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={signo.lower()}&day=today"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()

            horoscopo_en = data["data"]["horoscope_data"] 

            horoscopo_es = Translator(source='en', target='es').translate(horoscopo_en)

            if horoscopo_es:
                self.bot.send_message(chat_id, f"🔮 Tu horóscopo para hoy es:\n\n{horoscopo_es}")
            else:
                self.bot.send_message(chat_id, "No pude obtener tu horóscopo en este momento.")
        except Exception as e:
            print(f"⚠️ Error al obtener horóscopo: {e}")
            self.bot.send_message(chat_id, "No pude obtener tu horóscopo en este momento.")
        
        self.router.menu.mostrar_menu(chat_id)
