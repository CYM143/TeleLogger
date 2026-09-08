import telebot
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv
import asyncio, os

load_dotenv()
bot = AsyncTeleBot(os.getenv('API'))

@bot.message_handler(commands=['start'])
async def start_handler(message):
    await bot.send_message(message.chat.id, "I'm alive !")


async def main():
    await bot.infinity_polling()

asyncio.run(main())