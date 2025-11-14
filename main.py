from threading import Thread
from flask import Flask, request
from core.google_auth import GoogleAuthService
from dotenv import load_dotenv
from core.bot import TelegramBotHandler


load_dotenv()

# Servidor Flask para OAuth
app = Flask(__name__)
google_auth = GoogleAuthService()

@app.route("/oauth2/callback")
def oauth_callback():
    code = request.args.get("code")
    chat_id = request.args.get("state")

    if not code or not chat_id:
        return "<h3>❌ Faltan parámetros en la respuesta de Google.</h3>", 400

    try:
        tokens = google_auth.intercambiar_code_por_tokens(code)
        google_auth.guardar_tokens_para_usuario(chat_id, tokens)
        return "<h3>✅ Tu cuenta de Google Calendar fue conectada correctamente. Ya podés volver al bot.</h3>"
    except Exception as e:
        print(f"⚠️ Error en el callback OAuth: {e}")
        return "<h3>❌ Error al conectar tu cuenta de Google.</h3>", 500

def iniciar_flask():
    app.run(port=5000, debug=False)

# Main
if __name__ == "__main__":
    Thread(target=iniciar_flask).start()
    bot = TelegramBotHandler()
    bot.iniciar()