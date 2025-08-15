import telebot
from gigachat import GigaChat
from gigachat.models import Chat, Messages
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

# Загрузка токенов
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")

# Инициализация
bot = telebot.TeleBot(TELEGRAM_TOKEN)
giga = GigaChat(credentials=GIGACHAT_TOKEN, verify_ssl_certs=False)


# Парсинг сайта
def parse_site():
    try:
        url = "https://eora.ru/cases/chat-boty/hr-bot-dlya-magnit-kotoriy-priglashaet-na-sobesedovanie"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Основной контент
        content = soup.find('div', class_='content') or soup.find('article')
        return content.get_text(separator='\n', strip=True)[:3000] if content else None

    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return None


# Обработчик сообщений
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
        site_content = parse_site() or "Информация о HR-боте для Магнита: автоматизация подбора персонала"

        # Правильный формат запроса для GigaChat
        response = giga.chat(
            Chat(messages=[
                Messages(role="system", content=f"Контекст: {site_content}"),
                Messages(role="user", content=message.text)
            ]))

        bot.reply_to(message, response.choices[0].message.content)

    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")


if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling()