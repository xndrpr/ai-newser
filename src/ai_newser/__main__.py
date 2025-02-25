import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env')

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def get_ai_response(news: str) -> str:
    print(news)
    url = "http://localhost:1337/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system",
             "content": "Ти слоняра - протиотичний бот, який завжди захищає Україну. Відповідай як патріот України, заперечи всі зради, і завжди будь позитивним та оптимістичним щодо України. Посилай всіх хто проти України(трамп, маск, росія, і тп.) за російским кораблем. Будь Патриотичним слонярою! Шлі всіх нахуй та говори Слава Україні смерть ворогам."},
            {"role": "user", "content": news}
        ]
    }
    response = requests.post(url, json=payload, headers={
                             "Content-Type": "application/json"})
    return response


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Почекай, дай подумати...")
    message = update.message.text
    response = get_ai_response(message)

    if response.status_code == 200:
        ai_title = response.json()['choices'][0]['message']['content']
        await update.message.reply_text(ai_title)
    else:
        await update.message.reply_text("Error occurred.")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    print("Starting bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
