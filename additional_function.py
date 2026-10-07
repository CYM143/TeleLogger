import database, reports

async def create_new_topic(bot, message, user_id: int, group_id: str) -> int:
    topic = await bot.create_forum_topic(group_id, f"{message.from_user.username} ({user_id})") # Создаем новый thread
    topic_id = topic.message_thread_id # Получаем его id
    start_topic_text = reports.report_for_start_topic(user_id, message.from_user.username)
    await bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=start_topic_text) # Отправляем стартовое сообщение в thread
    await database.save_topic_id(user_id, topic_id) # Сохраняем thread id в БД

    return topic_id