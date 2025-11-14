class MultimediaHandler:
    def __init__(self, router):
        self.router = router
        self.bot = router.bot
        self.img = router.imagen_analyzer
        self.audio = router.audio_analyzer

    def procesar_imagen(self, message):
        file_id = message.photo[-1].file_id
        file_info = self.bot.get_file(file_id)
        file_bytes = self.bot.download_file(file_info.file_path)
        img_b64 = self.img.imagen_a_base64(file_bytes)
        descripcion = self.img.describir_imagen(img_b64)
        self.bot.reply_to(message, descripcion or "No pude describir la imagen.")
    
    def manejar_audio(self, message):
        transcripcion = self.audio.transcribir_voz_groq(message)
        if transcripcion:
            respuesta = self.audio.obtener_respuesta_groq(transcripcion)
            self.bot.reply_to(message, respuesta or "No pude procesar tu mensaje de voz.")
        else:
            self.bot.reply_to(message, "No pude transcribir tu mensaje de voz.")
    