import random
from funcionalidades_menu.foto_sorpresa import FotoSorpresa
from funcionalidades_menu.horoscopo import Horoscopo
from funcionalidades_menu.frase_inspiradora import FraseInspiradora


class SorpresaHandler:
    def __init__(self, router):
        self.router = router
        self.bot = router.bot

    def iniciar(self, call):
        chat_id = call.message.chat.id
        self.router.modos[chat_id] = "sorpresa"
        self.bot.send_message(chat_id, "¡Genial! Preparando una sorpresa especial para vos... 💫")

        opciones = ["foto", "horoscopo", "frase"]
        opcion = random.choice(opciones)

        try:
            # Lee el horóscopo
            if opcion == "horoscopo":
                self.bot.send_message(chat_id, "Hoy toca: Tu horóscopo del día 🔮")
                horoscopo = Horoscopo(self.bot, self.router)
                horoscopo.obtener_signo(call.message)
                return
            
            # Envia una foto random de animales
            elif opcion == "foto":
                foto_random = FotoSorpresa()
                imagen = foto_random.obtener_foto_random()
                captions = [
                    "¡Aquí tienes una sorpresa para alegrar tu día! 🐶",
                    "¡Mirá esta belleza! Espero que te saque una sonrisa 🩷",
                    "¡Un regalito visual para vos! Disfrutalo 🐾",
                    "¡Espero que esta imagen te alegre el día! 🌟",
                    "¡Una sorpresa especial solo para vos! 🐕"
                ]
                caption = random.choice(captions)

                self.bot.send_message(chat_id, "Hoy toca: Imagen random de animalitos 🐾")

                if imagen:
                    if imagen.endswith((".jpg", ".jpeg", ".png")):
                        self.bot.send_photo(chat_id, imagen, caption = caption)
                    elif imagen.endswith(".gif"):
                        self.bot.send_animation(chat_id, imagen, caption = caption)
                    elif imagen.endswith((".mp4", ".webm")):
                        self.bot.send_video(chat_id, imagen, caption = caption)
                    else: 
                        self.bot.send_photo(chat_id, imagen, caption = caption)
                else:
                    self.bot.send_message(chat_id, "¡No pude conseguir una foto esta vez, pero pronto lo intentaré de nuevo! 😊")
            
            else:
                frase_inspiradora = FraseInspiradora()
                frase = frase_inspiradora.obtener_frase_inspiradora()
                self.bot.send_message(chat_id, "Hoy toca: Frase inspiradora 🪷")
                self.bot.send_message(chat_id, frase, parse_mode="Markdown")
        
        except Exception as e:
                    print(f"⚠️ Error en opción sorpresa: {e}")
                    self.bot.send_message(chat_id, "Hubo un error al procesar tu solicitud 😕. Volviendo al menú principal.")
    
        self.router.modos[chat_id] = "menu"
        self.router.menu.mostrar_menu(chat_id)