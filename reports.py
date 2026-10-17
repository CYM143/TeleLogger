import html

def report_for_sent_message(text: str, is_admin: bool) -> str:
    """Function for report generation. Return formatted report."""
    if not is_admin:
        if text is not None:
            formatted_report = f"""Новое сообщение:

<blockquote>{html.escape(text)}</blockquote>"""
        else:
            formatted_report = f"Новое сообщение !"

    else:
        if text is not None:
            formatted_report = f"""Ваше новое сообщение:
        
<blockquote>{html.escape(text)}</blockquote>"""
        else:
            formatted_report = f"Ваше новое сообщение !"
        
    return formatted_report

def report_for_edited_message(text: str) -> str:
    """Function for edited message report generation. Return formatted report."""
    formatted_report = f"""Сообщение изменено ! 
Измененное содержание:
<blockquote>{html.escape(text)}</blockquote>
"""
    return formatted_report

def report_for_edited_message_but_original_message_not_found() -> str:
    """Function for edited report generation without original message. Return formatted report."""
    formatted_report = f"Сообщение изменено !\nОригинальное сообщение не найдено в базе данных !"
    return formatted_report

def reprort_for_deleted_message() -> str:
    """Function for deleted message report generation. Return formatted report."""
    formatted_report = f"Сообщение удалено !"
    return formatted_report

def report_for_delete_message_but_original_message_not_found() -> str:
    """Function for deleted message report generation withoout original message. Return formatted report."""
    formatted_report = f"Сообщение удалено !\nОригинальное сообщение не найдено в базе данных !"
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