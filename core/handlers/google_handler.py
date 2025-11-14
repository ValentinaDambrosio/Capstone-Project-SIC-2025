class GoogleAuthHandler:
    def __init__(self, router):
        self.router = router
        self.bot = router.bot
        self.google = router.google_auth
        self.calendar = router.google_calendar

    def iniciar(self, call):
        chat_id = call.message.chat.id
        # Verifica si el usuario ya tiene tokens almacenados; si los tiene, informar y no generar link
        tokens = self.google.obtener_tokens(chat_id)
        if tokens:
            self.bot.send_message(
                chat_id,
                "✅ Tu cuenta de Google ya está conectada y sincronizada con el calendario."
            )
            self.router.modos[chat_id] = "menu"
            self.router.menu.mostrar_menu(chat_id)
        else:
            link = self.google.generar_link_autorizacion(chat_id)
            self.bot.send_message(
                chat_id,
                f"Para conectar tu cuenta de Google y sincronizar tu ciclo con tu calendario, hacé click en el siguiente enlace:\n\n[🌷🔗 Conectar con mi calendario]({link})",
                parse_mode = "Markdown"
            )
            self.router.modos[chat_id] = "menu"
            self.router.menu.mostrar_menu(chat_id)