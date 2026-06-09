import telebot

from config import API_TOKEN

if not API_TOKEN:
    raise ValueError("API_KEY is empty or missing. Check your .env file")

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def main(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")

bot.polling(non_stop=True)
