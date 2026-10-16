import database, reports, asyncio
from telebot.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio

media_massive = {}
content_types = {
    'photo': (lambda m: m.photo[-1].file_id, InputMediaPhoto),
    'video': (lambda m: m.video.file_id, InputMediaVideo),
    'document': (lambda m: m.document.file_id, InputMediaDocument),
    'audio': (lambda m: m.audio.file_id, InputMediaAudio)
}

async def create_new_topic(bot, message, user_id: int, group_id: str) -> int:
    topic = await bot.create_forum_topic(group_id, f"{message.from_user.username} ({user_id})") # Создаем новый thread
    topic_id = topic.message_thread_id # Получаем его id
    start_topic_text = reports.report_for_start_topic(user_id, message.from_user.username)
    await bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=start_topic_text) # Отправляем стартовое сообщение в thread
    await database.save_topic_id(user_id, topic_id) # Сохраняем thread id в БД

    return topic_id

async def proccess_input_media(message) -> list:
    if message.media_group_id not in media_massive: # Проверяем существует ли уже массив с данными по этой меди группе
        media_massive[message.media_group_id] = []

    get_id_func, media_class = content_types[message.content_type] # Получаем тип файла и его класс (InputMedia)
    file_id = get_id_func(message) # Получаем id файла для отправки

    media_massive[message.media_group_id].append((media_class, file_id, message.caption)) # Добавляем сообщение в массив + текст под сообщением
    
    current_len = len(media_massive[message.media_group_id]) # Получаем текущую длинну списка

    await asyncio.sleep(0.5) # Ждем, дабы получить остальные файлы
    
    if current_len == len(media_massive[message.media_group_id]): # Если длинна не изменилась, значит элемент последний
        end_media = [] # Создаем временный массив с файлами, чтобы удалить постоянный
        caption = None

        for _, _, capt in media_massive[message.media_group_id]: # Перебираем все тексты под сообщениями дабы найти нужный
            if capt:
                caption = capt
                break

        report = reports.report_for_sent_message(caption) # Формируем отчет

        for i, (m_class, f_id, _) in enumerate(media_massive[message.media_group_id]): # Перебираем классы (InputMedia) и их id для отправки
            if i == 0: # Если это первый элемент привязываем к нему текст
                end_media.append(m_class(f_id, caption=report, parse_mode="HTML")) 
            else: # Добавляем остальные элементы без текста
                end_media.append(m_class(f_id)) 

        del media_massive[message.media_group_id] # Удаляем из памяти массив с медиа

        return end_media # Возвращаем массив с медиа (временный)
    
    return None
