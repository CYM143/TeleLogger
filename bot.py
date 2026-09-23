import telebot
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv, set_key
import asyncio, os
import reports, database

load_dotenv()
bot = AsyncTeleBot(os.getenv('API'))

@bot.message_handler(commands=['start']) # Обработка команды /start
async def start_handler(message):
    user_id = message.chat.id
    admin_id = os.getenv('admin_id') # Получаем данные из .env

    if admin_id is not None and admin_id != str(user_id): # Если админ уже есть и это не он, то отклоняем запрос.
        await bot.send_message(user_id, 'Извините, этот бот для вас недоступен !')
        return
    elif admin_id == str(user_id): # Если админ уже есть и это он, то возвращаем сообщение о том, что бот работает.
        await bot.send_message(user_id, "Я в сети и работаю в штатном режиме !")
    else: # Если админа нет, то устанавливаем этот аккаунт, как аккаунт администратора.
        set_key('.env', 'admin_id', str(user_id))
        await bot.send_message(user_id, "Вы успешно установили этот аккаунт, как аккаунт администратора !")
        return

@bot.message_handler(commands=['stats']) # Обработка команды /stats
async def statistic_handler(message):
    user_id = message.from_user.id
    admin_id = int(os.getenv('admin_id'))

    if user_id != admin_id: # Пропускаем все запросы не от администратора.
        return

    stats = await database.get_statistic() # Получение статистики из БД.

    await bot.send_message(user_id, f"Статистика:\n\nСохранено чатов - {stats[0]}\nВсего сообщений - {stats[1]}") # Отправляем отчет.

@bot.business_message_handler(func=lambda message: True, content_types=['text']) # Обработка всех текстовых сообщений
async def message_text_forwarder(message):
    admin_id = int(os.getenv('admin_id'))
    user_id = message.from_user.id

    if user_id == admin_id: # Если это сообщение админа - пропускаем.
        return

    report = reports.report_for_sent_message(message.from_user.id, message.from_user.username, message.text) # Формируем отчет о сообщении (от кого, какое содержание)
    bot_msg = await bot.send_message(admin_id, report, parse_mode='HTML')
    await database.save_message(user_id, bot_msg.message_id, message.message_id) # Сохраняем id сообщений в БД.

@bot.business_message_handler(func=lambda message: True, content_types=['photo', 'video', 'document', 'audio']) # Обработка всех медиа к которым можно прикрепить текстовое сообщение.
async def message_files_forwarder(message):
    admin_id = int(os.getenv('admin_id'))
    user_id = message.from_user.id

    if user_id == admin_id: # Если это сообщение админа - пропускаем.
        return

    report = reports.report_for_sent_message(user_id, message.from_user.username, message.caption) # Формируем текстовый отчет для сообщения (исходя из формата файла)

    # Выбираем формат файла и исходя из него отправляем сообщение.
    if message.content_type == 'photo':
        bot_msg = await bot.send_photo(admin_id, message.photo[-1].file_id, caption=report, parse_mode='HTML')
    elif message.content_type == 'video':
        bot_msg = await bot.send_video(admin_id, message.video[-1].file_id, caption=report, parse_mode='HTML')
    elif message.content_type == 'document':
        bot_msg = await bot.send_document(admin_id, message.document.file_id, caption=report, parse_mode='HTML')
    elif message.content_type == 'audio':
        bot_msg = await bot.send_audio(admin_id, message.audio.file_id, caption=report, parse_mode='HTML')

    await database.save_message(user_id, bot_msg.message_id, message.message_id) # Сохраняем id сообщений в БД.

@bot.business_message_handler(func=lambda message: True, content_types=['voice', 'video_note']) # Обработка всех медиа к которым нельзя прикрепить текстовое сообщене.
async def message_media_forwarder(message):
    admin_id = int(os.getenv('admin_id'))
    user_id = message.from_user.id

    if user_id == admin_id: # Если это сообщение админа - пропускаем.
        return

    report = reports.report_for_sent_message(user_id, message.from_user.username, message.caption)# Формируем текстовый отчет для сообщения.

    # Выбирвем формат файла и отправляем отчет.
    if message.content_type == 'voice':
        bot_msg = await bot.send_audio(admin_id, message.voice.file_id, caption=report, parse_mode="HTML")
    elif message.content_type == 'video_note':
        bot_msg = await bot.send_video(admin_id, message.video_note.file_id)
        await bot.reply_to(bot_msg, text=report) # Отвечаем на видео-сообщение тк напрямую добавить текстовое сообщение не получится.

    await database.save_message(user_id, bot_msg.message_id, message.message_id) # Сохраняем id сообщений в БД.

@bot.edited_business_message_handler(func=lambda message: True) # Обработка отредактированных сообщений.
async def message_edited(message):
    admin_id = int(os.getenv('admin_id'))
    user_id = message.from_user.id

    if user_id == admin_id: # Если это сообщения админа - пропускаем.
        return

    original_message_id = await database.get_message_id_from_bot_chat(user_id, message.message_id) # Получаем id сообщения бота для оригинального сообщения.
    if original_message_id is None: # Проверяем нашлись ли оригиналы сообщений.
        report = reports.report_for_edited_message_but_original_message_not_found(user_id, message.from_user.username) # Формируем отчет.
        await bot.send_message(admin_id, report)
        return
    report = reports.report_for_edited_message(user_id, message.from_user.username, message.text) # Формируем отчет.
    bot_msg = await bot.send_message(admin_id, report, reply_to_message_id=original_message_id, parse_mode="HTML")
    await database.save_message(user_id, bot_msg.message_id, message.message_id) # Пересохраняем новое id сообщения бота.

@bot.deleted_business_messages_handler(func=lambda message: True) # Обработка удаленных сообщений.
async def message_deleted(message):
    admin_id = int(os.getenv('admin_id'))
    user_id = message.chat.id

    if user_id == admin_id: # Если это сообщения админа - пропускаем.
        return

    message_ids = message.message_ids # Получаем id удаленных сообщений.
    for message_id in message_ids: # Перебираем все id.
        original_message_id = await database.get_message_id_from_bot_chat(user_id, message_id) # Получаем id сообщения бота для оригинального сообщения.
        if original_message_id is None: # Проверяем нашлись ли оригиналы сообщений.
            report = reports.report_for_delete_message_but_original_message_not_found(user_id, message.chat.username) # Формируем отчет.
            await bot.send_message(admin_id, report)
        else:
            report = reports.reprort_for_deleted_message(user_id, message.chat.username) # Формируем отчет.
            await bot.send_message(admin_id, report, reply_to_message_id=original_message_id) 

async def main():
    print('Bot is now online.')
    await bot.infinity_polling()

asyncio.run(main())