import telebot
from telebot import types

from config import API_TOKEN
from pipeline.stats_visualisation import statistic
from utils import io

if not API_TOKEN:
    raise ValueError("API_KEY is empty or missing. Check your .env file")

bot = telebot.TeleBot(API_TOKEN)
png_handler = io.PngFigureHandler()
stats_handler = io.JsonFileHandler("stats")

TOPIC_TRANSLATION = {
    "entertainment": "Развлечения",
    "incidents": "Происшествия",
    "weather": "Погода",
    "art": "Искусство",
    "education": "Образование",
    "memes": "Мемы",
    "war": "Военные действия",
    "celebrities": "Знаменитости",
    "food": "Еда",
    "politics": "Политика",
    "healthcare": "Здравоохранение",
    "culture": "Культура",
    "sports": "Спорт",
    "economics": "Экономика",
    "city-life": "Городская жизнь",
    "science-and-technology": "Наука и технологии",
    "miscellaneous": "Разное"
}

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
    try:
        topic, topic_frequency = statistic.get_topic_frequencies(top_n=1)[0]
        person, person_frequency = statistic.get_person_frequencies(top_n=1)[0]
        word, word_frequency = statistic.get_word_frequencies(top_n=1)[0]
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("digest.png", png_handler.load("digest")),
            caption=(
                "дайджест\n\n"
                f"Самая популярная тема - '{TOPIC_TRANSLATION[topic]}'\n"
                f"Всего упоминалась в {topic_frequency} cтатье(ях)\n\n"
                f"Из личностей больше всех встречался - {person}\n"
                f"Упомянули {person_frequency} раз\n\n"
                f"Чаше всего встречалось слово - '{word}'\n"
                f"Встретилось целых {word_frequency} раз\n\n"
                f"Последние новости:\n"
                f"{statistic.get_fresh_news_text(top_n=3)}"
            ),
            reply_markup=get_markup()
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "К сожалению, пока недостаточно данных. Попробуйте снова поже",
            reply_markup=get_markup()
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "популярные темы")
def popular_topics(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("topic_frequencies.png", png_handler.load("topic_frequencies")),
            caption=(
                "Топ популярных тем новостей:\n\n" +
                "\n".join(
                    f"{i}. {TOPIC_TRANSLATION[topic]} — {count}"
                    for i, (topic, count) in enumerate(statistic.get_topic_frequencies(), start=1)
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
    bot.send_message(
        message.chat.id,
        "Свежие новости на сегодня:\n\n"
        f"{statistic.get_fresh_news_text()}",
        reply_markup=get_markup()
    )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "личность дня")
def top_person(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("person_frequencies.png", png_handler.load("person_frequencies")),
            caption=(
                "Топ популярных личностей:\n\n" +
                "\n".join(
                    f"{i}. {person} — {count}"
                    for i, (person, count) in enumerate(statistic.get_person_frequencies(), start=1)
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
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("word_frequencies.png", png_handler.load("word_frequencies")),
            caption=(
                "Топ популярных слов:\n\n" +
                "\n".join(
                    f"{i}. {word} — {count}"
                    for i, (word, count) in enumerate(statistic.get_word_frequencies(), start=1)
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
