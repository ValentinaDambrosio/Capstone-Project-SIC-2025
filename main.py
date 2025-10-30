from dotenv import load_dotenv
from core.bot import TelegramBotHandler

load_dotenv()

if __name__ == "__main__":
    bot = TelegramBotHandler()
    bot.iniciar()