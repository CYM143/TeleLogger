def report_for_sent_message(user_id: int, username: str, text: str) -> str:
    """Function for report generation. Return formatted report."""
    if text is not None:
        formatted_report = f"""Сообщение от @{username} ({user_id}):

<blockquote>{text}</blockquote>"""
    else:
        formatted_report = f"""Сообщение от @{username} ({user_id})"""
        
    return formatted_report

def report_for_edited_message(user_id: int, username: str, text: str) -> str:
    """Function for edited message report generation. Return formatted report."""
    formatted_report = f"""Сообщение изменено ! Чат @{username} ({user_id})

Измененное содержание:
<blockquote>{text}</blockquote>
"""
    return formatted_report

def report_for_edited_message_but_original_message_not_found(user_id: int, username: str) -> str:
    """Function for edited report generation without original message. Return formatted report."""
    formatted_report = f"""Сообщение изменено ! Чат @{username} ({user_id})

Оригинальное сообщение не найдено в базе данных !
"""
    return formatted_report

def reprort_for_deleted_message(user_id: int, username: str) -> str:
    """Function for deleted message report generation. Return formatted report."""
    formatted_report = f"Сообщение удалено ! Чат @{username} ({user_id})"
    return formatted_report

def report_for_delete_message_but_original_message_not_found(user_id: int, username: str) -> str:
    """Function for deleted message report generation withoout original message. Return formatted report."""
    formatted_report = f"""Сообщение удалено ! Чат @{username} ({user_id})

Оригинальное сообщение не найдено в базе данных !
"""
    return formatted_report

def report_for_start_topic(user_id: int, username: str) -> str:
    """Function for start topic report generation. Return formatted report."""
    formatted_report = f"Начата новая ветка для @{username} ({user_id})"

    return formatted_report

def report_for_statistic(chat_count: int, records_count: int) -> str:
    """Function for statistic report generation. Return formatted report."""
    formatted_report = f"""*Статистика сохранения чатов:*
Сохранено чатов: {chat_count}
Всего сохранено сообщений: {records_count}
"""

    return formatted_report