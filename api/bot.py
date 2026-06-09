import telebot
from telebot import types

from config import API_TOKEN

if not API_TOKEN:
    raise ValueError("API_KEY is empty or missing. Check your .env file")

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup()

    button_digest = types.KeyboardButton("Дайджест")
    button_topics_popular = types.KeyboardButton("Популярные новости")
    button_topics_fresh = types.KeyboardButton("Свежие новости")
    button_top_person = types.KeyboardButton("Личность дня")
    button_top_word = types.KeyboardButton("Слово дня")
    
    markup.row(button_digest)
    markup.row(button_topics_fresh, button_topics_popular)
    markup.row(button_top_person, button_top_word)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Чем я могу сегодня помочь?",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "дайджест")
def digest(message):
    bot.send_message(message.chat.id, "Дайджест")

@bot.message_handler(func=lambda message: message.text.lower().strip() == "свежие новости")
def fresh_news(message):
    bot.send_message(message.chat.id, "Свежие новости")

@bot.message_handler(func=lambda message: message.text.lower().strip() == "популярные новости")
def top_news(message):
    bot.send_message(message.chat.id, "Популярные новости")

@bot.message_handler(func=lambda message: message.text.lower().strip() == "личность дня")
def top_person(message):
    bot.send_message(message.chat.id, "Топ личность")

@bot.message_handler(func=lambda message: message.text.lower().strip() == "слово дня")
def top_word(message):
    bot.send_message(message.chat.id, "Топ слово")


@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.send_message(message.chat.id, "Я вас не понял. Пожалуйста, воспользуйтесь кнопками меню.")

bot.polling(non_stop=True)
