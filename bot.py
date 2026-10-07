import telebot
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv, set_key
import asyncio, os
import reports, database
import additional_function as add_func

load_dotenv()
bot = AsyncTeleBot(os.getenv('API'))

@bot.message_handler(commands=['start']) # Обработка команды /start
async def start_handler(message):
    user_id = message.from_user.id # Получаем id того, кто написал
    admin_id = os.getenv('admin_id') # Получаем id админа

    if admin_id == str(user_id): # Если пишет вдмин, возвращаем, что бот в сети
        await bot.send_message(user_id, 'Бот в сети !')
    elif admin_id is None: # Если админа нет, устанавливаем нового
        set_key('.env', 'admin_id', str(user_id)) # Устанавливаем значения id админа 
        load_dotenv(override=True) # Обновляем все значения .env в памяти 
        await bot.send_message(user_id, "Ваш аккаунт был установлен, как аккаунт администратора !")
    else: # Иначе делаем вид, что бот не рабочий
        return

@bot.message_handler(commands=['status']) # Обработка команды /status
async def status_handler(message):
    user_id = message.from_user.id
    admin_id = os.getenv('admin_id')

    if admin_id == str(user_id): # Если пишет админ, проверяем сохраняет ли бот сообщения
        group_id = os.getenv('group_id') # Получаем group_id

        if group_id is not None: # Если group_id есть, то бот работает
            await bot.send_message(user_id, 'Бот в сети и работает штатно !')
        else: # Если же нету, то бот не может сохранять сообщения
            await bot.send_message(user_id, 'Бот не подключен к группе с включенными темами, испольуйте /set_group')

    else: # Если пишет не админ, делаем вид, что бот не рабочий
        return

@bot.message_handler(commands=['stats']) # Обработка команды /stats
async def statistic_handler(message):
    user_id = message.from_user.id
    admin_id = os.getenv('admin_id')

    if admin_id == str(user_id): # Если пишет админ, получаем и отправляем статистику бота
        stats = await database.get_statistic() # Получаем статистику из ДБ
        report = reports.report_for_statistic(stats[0], stats[1]) # Формируем отчет

        await bot.send_message(user_id, report, parse_mode='Markdown')

    else: # Если пишет не админ, то делаем вид, что бот не рабочий
        return

@bot.message_handler(commands=['set_group']) # Обработка команды /set_group
async def set_group(message):
    user_id = message.from_user.id
    admin_id = os.getenv('admin_id')

    if admin_id != str(user_id): # Проверяем админ ли использовал команду
        return

    if message.chat.is_forum: # Проверяем включены ли threads в группе

        bot_info = await bot.get_me()
        bot_chat_member = await bot.get_chat_member(message.chat.id, bot_info.id) # Получаем бота как пользователя группы
        if bot_chat_member.status in ['administrator', 'creator']: # Проверяем является ли бот администратором
            if bot_chat_member.can_manage_topics: # Проверяем есть ли у бота разрешение на редактирование threads
                set_key('.env', 'group_id', str(message.chat.id)) # Устанавливаем значения id группы для уведомлений
                load_dotenv(override=True) # Обновляем все значения .env в памяти
                await bot.reply_to(message, "Эта группа установлена для уведомлений !")
                await bot.send_message(message.from_user.id, f"Установлена новая группа для уведомлений !\n*Название:* {message.chat.title}\n*ID группы:* {message.chat.id}", parse_mode='Markdown')
            else:
                await bot.reply_to(message, 'У меня нет прав на редактирование тем !')
        else:
            await bot.reply_to(message, 'У меня нет прав администратора !')

    else: # Если threads нету, просим пользователя их включить
        await bot.reply_to(message, "Внимание !\nВ группе должны быть включены темы.")


@bot.business_message_handler(func=lambda message: True, content_types=['text']) # Обработка всех текстовых сообщений
async def message_text_forwarder(message):
    user_id = message.from_user.id
    group_id = os.getenv('group_id')

    if not group_id: # Если группы для уведомлений ещё нет
        admin_id = os.getenv('admin_id') # Получаем id админа и отправляем ему оповещение
        await bot.send_message(admin_id, 'Внимание бот получил сообщение, но не смог его сохранить, установите группу для уведомлений через /set_group')
        return
    
    topic_id = await database.search_topic_id(user_id) # Ищем thread id в БД
    if not topic_id: # Если thread id не найден
        topic_id = await add_func.create_new_topic(bot, message, user_id, group_id) # Создаём новый thread для отчетов
    
    report = reports.report_for_sent_message(message.text) # Формируем отчет по сообщению
    bot_msg = await bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=report, parse_mode='HTML')
    await database.save_message(user_id, bot_msg.message_id, message.message_id) # Сохраняем id сообщений в БД.

'''
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
'''
@bot.edited_business_message_handler(func=lambda message: True) # Обработка отредактированных сообщений.
async def message_edited(message):
    user_id = message.from_user.id
    group_id = os.getenv('group_id')

    if not group_id:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, 'Внимание бот получил изменение сообщения, но не смог его отобразить, установите группу для уведомлений через /set_group')
        return

    topic_id = await database.search_topic_id(user_id) # Ищем thread id в БД
    if not topic_id: # Если thread id не найден
        topic_id = await add_func.create_new_topic(bot, message, user_id, group_id) # Создаем новый thread для отчетов

    original_message_id = await database.get_message_id_from_bot_chat(user_id, message.message_id) # Получаем id сообщения бота для оригинального сообщения.
    if original_message_id is None: # Проверяем нашлись ли оригиналы сообщений.
        report = reports.report_for_edited_message_but_original_message_not_found() # Формируем отчет.
        await bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=report)
        return
    
    report = reports.report_for_edited_message(message.text) # Формируем отчет.
    bot_msg = await bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=report, reply_to_message_id=original_message_id, parse_mode="HTML")
    await database.save_message(user_id, bot_msg.message_id, message.message_id) # Пересохраняем новое id сообщения бота.

@bot.deleted_business_messages_handler(func=lambda message: True) # Обработка удаленных сообщений.
async def message_deleted(message):
    user_id = message.from_user.id
    group_id = os.getenv('group_id')

    if not group_id:
        admin_id = os.getenv('admin_id')
        await bot.send_message(admin_id, 'Внимание бот получил изменение сообщения, но не смог его отобразить, установите группу для уведомлений через /set_group')
        return

    topic_id = await database.search_topic_id(user_id) # Ищем thread id в БД
    if not topic_id: # Если thread id не найден
        topic_id = await add_func.create_new_topic(bot, message, user_id, group_id) # Создаем новый thread для отчетов

    message_ids = message.message_ids # Получаем id удаленных сообщений.
    for message_id in message_ids: # Перебираем все id.
        original_message_id = await database.get_message_id_from_bot_chat(user_id, message_id) # Получаем id сообщения бота для оригинального сообщения.
        if original_message_id is None: # Проверяем нашлись ли оригиналы сообщений.
            report = reports.report_for_delete_message_but_original_message_not_found() # Формируем отчет.
            await bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=report)
        else:
            report = reports.reprort_for_deleted_message() # Формируем отчет.
            await bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=report, reply_to_message_id=original_message_id) 
            
async def main():
    await database.init_db()
    print('Bot is now online.')
    await bot.infinity_polling()

asyncio.run(main())