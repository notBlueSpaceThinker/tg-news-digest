from datetime import datetime

import telebot
from telebot import types

from config import API_TOKEN
from utils import io

if not API_TOKEN:
    raise ValueError("API_KEY is empty or missing. Check your .env file")

bot = telebot.TeleBot(API_TOKEN)
png_handler = io.PngFigureHandler()
stats_handler = io.JsonFileHandler("stats")

def get_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup()
    button_digest = types.KeyboardButton("Дайджест")
    button_topics = types.KeyboardButton("Популярные темы")
    button_news_fresh = types.KeyboardButton("Свежие новости")
    button_top_person = types.KeyboardButton("Личность дня")
    button_top_word = types.KeyboardButton("Слово дня")
    markup.row(button_digest)
    markup.row(button_topics, button_news_fresh)
    markup.row(button_top_person, button_top_word)
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Чем я могу сегодня помочь?",
        reply_markup=get_markup()
    )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "дайджест")
def digest(message):
    bot.send_message(message.chat.id, "Дайджест")

@bot.message_handler(func=lambda message: message.text.lower().strip() == "популярные темы")
def popular_topics(message):
    try:
        topic_frequencies = stats_handler.load("topic_frequencies", load_hashed=False)
        topic_frequencies = dict(
            sorted(
                topic_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        )
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("topic_frequencies.png", png_handler.load("topic_frequencies")),
            caption=(
                "Топ популярных тем новостей:\n\n" +
                "\n".join(
                    f"{i}. {topic} — {count}"
                    for i, (topic, count) in enumerate(topic_frequencies.items(), start=1)
                )
            ),
            reply_markup=get_markup()
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "К сожалению, пока недостаточно данных. Попробуйте снова поже",
            reply_markup=get_markup()
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "свежие новости")
def fresh_news(message):
    fresh_news = stats_handler.load("fresh_news", load_hashed=False)
    send_message_list = []
    urls = []
    for key in sorted(fresh_news.keys(), key=lambda k: int(k)):
        meta = fresh_news[key]
        send_message_list.append(f"{key}. {meta["portal"]}: {meta["title"]}")
        curr_time = datetime.fromisoformat(meta["date"]).time()
        send_message_list.append(f"Время публикации: {curr_time}\n")
        urls.append(meta["url"])
    send_message_txt = "\n".join(send_message_list)
    bot.send_message(
        message.chat.id,
        "Свежие новости на сегондя:\n\n"
        f"{send_message_txt}",
        reply_markup=get_markup()
    )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "личность дня")
def top_person(message):
    try:
        person_frequencies = stats_handler.load("person_frequencies", load_hashed=False)
        person_frequencies = dict(
            sorted(
                person_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        )
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("person_frequencies.png", png_handler.load("person_frequencies")),
            caption=(
                "Топ популярных личностей:\n\n" +
                "\n".join(
                    f"{i}. {person} — {count}"
                    for i, (person, count) in enumerate(person_frequencies.items(), start=1)
                )
            ),
            reply_markup=get_markup()
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "К сожалению, пока недостаточно данных. Попробуйте снова поже",
            reply_markup=get_markup()
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "слово дня")
def top_word(message):
    try:
        word_frequencies = stats_handler.load("word_frequencies", load_hashed=False)
        word_frequencies = dict(
            sorted(
                word_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        )
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("word_frequencies.png", png_handler.load("word_frequencies")),
            caption=(
                "Топ популярных личностей:\n\n" +
                "\n".join(
                    f"{i}. {word} — {count}"
                    for i, (word, count) in enumerate(word_frequencies.items(), start=1)
                )
            ),
            reply_markup=get_markup()
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "К сожалению, пока недостаточно данных. Попробуйте снова поже",
            reply_markup=get_markup()
        )

@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.send_message(
        message.chat.id,
        "Я вас не понял. Пожалуйста, воспользуйтесь кнопками меню.",
        reply_markup=get_markup()
    )
