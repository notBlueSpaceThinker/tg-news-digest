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
    button_bigram = types.KeyboardButton("Биграммы")
    button_trigram = types.KeyboardButton("Триграммы")
    button_logdice = types.KeyboardButton("Логдайс")
    markup.row(button_digest)
    markup.row(button_topics, button_news_fresh)
    markup.row(button_top_person, button_top_word)
    markup.row(button_bigram, button_trigram, button_logdice)
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"*Дарова, {message.from_user.first_name}!*\n"
        "*Я умею тоси-боси, муси-пуси..*\n"
        "*Новости короче выдаю :/*\n\n"
        "Вот список моих команд\n"
        "• *Дайджест* - типо сводка всего и вся.\n"
        "• *Популярные темы* - то, о чем сегодня трындычут везде\n"
        "• *Свежие новости* - ещё не разлетевшиеся, горяченькие посты\n"
        "• *Личность дня* - ну, они сегодня на слуху много где\n"
        "• *Слово дня* - пополняем лексикон\n\n"
        "спрашивай /help, если ещё понадоблюсь",
        reply_markup=get_markup(),
        parse_mode="Markdown"
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
                "*Так так так.. что там у нас вообще в мире-то творится*\n"
                "*Это дайджест, деткааа*\n\n"
                f"Та самая фигня о которой все говорят - '*{TOPIC_TRANSLATION[topic]}*'\n"
                f"Всего {topic_frequency} статей об этом\n\n"
                f"В общем.. Сегодня я вижу везде и всюду - *{person}*...    "
                f"Целых {person_frequency} раз мне попался(ась)\n\n"
                f"Сегодня больше всего мне попалось слово - *'{word}*'\n"
                f"Встретилось целых {word_frequency} раз (ёмоё)\n\n"
                f"Последние новости для тебя, дорогуша:\n"
                f"{statistic.get_fresh_news_text(top_n=3)}"
            ),
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "Подожди... У меня сейчас завал. Дай мне немного времени откиснуть.",
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "популярные темы")
def popular_topics(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("topic_frequencies.png", png_handler.load("topic_frequencies")),
            caption=(
                "*Вот и об этом у нас сегодня в народе глаголят:*\n\n" +
                "\n".join(
                    f"{i}. {TOPIC_TRANSLATION[topic]} — {count}"
                    for i, (topic, count) in enumerate(statistic.get_topic_frequencies(), start=1)
                )
            ),
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "К сожалению, пока недостаточно данных. Давай ты немного покимаришь там..",
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "свежие новости")
def fresh_news(message):
    bot.send_message(
        message.chat.id,
        "*Самый свежак для тебя достал:*\n\n"
        f"{statistic.get_fresh_news_text()}",
        reply_markup=get_markup(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "личность дня")
def top_person(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("person_frequencies.png", png_handler.load("person_frequencies")),
            caption=(
                "*О них говорит весь Нижний:*\n\n" +
                "\n".join(
                    f"{i}. {person} — {count}"
                    for i, (person, count) in enumerate(statistic.get_person_frequencies(), start=1)
                )
            ),
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "Да не тыкай ты, итак заказов много. Встань в очередь и жди",
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "слово дня")
def top_word(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("word_frequencies.png", png_handler.load("word_frequencies")),
            caption=(
                "*Вот такие слова я сегодня надыбал:*\n\n" +
                "\n".join(
                    f"{i}. {word} — {count}"
                    for i, (word, count) in enumerate(statistic.get_word_frequencies(), start=1)
                )
            ),
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "Мальчик, перезвони позже",
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "биграммы")
def bigrams(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("bigrams.png", png_handler.load("2gram_frequencies")),
            caption=(
                "*Биграммы:*\n\n" +
                "\n".join(
                    f"{i}. {words} — {count}"
                    for i, (words, count) in enumerate(statistic.get_ngram_frequencies(2, top_n=5), start=1)
                )
            ),
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "Да не тыкай ты, итак заказов много. Встань в очередь и жди",
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "триграммы")
def trigrams(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("trigrams.png", png_handler.load("3gram_frequencies")),
            caption=(
                "*Триграммы:*\n\n" +
                "\n".join(
                    f"{i}. {words} — {count}"
                    for i, (words, count) in enumerate(statistic.get_ngram_frequencies(3, top_n=5), start=1)
                )
            ),
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "Да не тыкай ты, итак заказов много. Встань в очередь и жди",
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.text.lower().strip() == "логдайс")
def logdice(message):
    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=("logdice_scores.png", png_handler.load("logdice_scores")),
            caption=(
                "*Логдайс:*\n\n" +
                "\n".join(
                    f"{i}. {words} — {logdice}"
                    for i, (words, logdice) in enumerate(statistic.get_logdice_scores(top_n=5), start=1)
                )
            ),
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )
    except FileNotFoundError:
        bot.send_message(
            message.chat.id,
            "Да не тыкай ты, итак заказов много. Встань в очередь и жди",
            reply_markup=get_markup(),
            parse_mode="Markdown"
        )

@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(
        message.chat.id,
        "Мой хороший.. Ты чего, вообще не андерстенд?\n"
        "Ладно, давай поподробнее\n\n"
        "• *Дайджест* - Общая сводка по разным направлениям. "
        "Самые последние или самые частотные данные\n\n"
        "• *Популярные темы* - различные тематики новостей. "
        "Цифры под ними - количество новостей которые относятся "
        "к той или иной тематике\n\n"
        "• *Свежие новости* - список новостей, которые появились"
        "за последнее время\n\n"
        "• *Личность дня* - имена и фамилии тех людей, которые "
        "были упомянуты в СМИ\n\n"
        "• *Слово дня* - слово, которое было самым употребляемым "
        "за сегодня\n"
        "(Предварительно мы взяли текста новостей очистили и лемматизировали)\n\n"
        "Все, надеюсь ты теперь андерстенд\n"
        "_Если остались вопросы - пиши @ILoveWatermelones_",
        reply_markup=get_markup(),
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.send_message(
        message.chat.id,
        "Ты че сейчас выпалил? Я не разобрал единого слова\n"
        "*Воспользуйся кнопками меню*\n\n"
        "_Или попробуй прокричать о помощи_ \help",
        reply_markup=get_markup(),
        parse_mode="Markdown"
    )
