import telebot
import requests
from bs4 import BeautifulSoup

bot_token = "ваш токен"  # вставьте сюда токен вашего бота
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Напиши /news, чтобы получить новости")

@bot.message_handler(commands=['news'])
def send_news(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('1. Спорт', '2. Технологии', '3. Наука')
    bot.send_message(message.chat.id, "Выбери категорию новостей:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def get_news(message):
    chat_id = message.chat.id
    if message.text == "1. Спорт":
        url = "https://www.sport-express.ru/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        news_list = soup.find_all("div", class_="se21-all-news-item__name")
        for news in news_list[:5]:
            bot.send_message(chat_id, news.text)
bot.polling()