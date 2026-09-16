import aiosqlite
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
database_name = os.getenv('database_name')

async def init_db() -> None:
    """Function for init DataBase"""
    async with aiosqlite.connect(database_name) as db:
        await db.commit()

async def save_message(user_id: int, bot_message_id: int, chat_message_id: int) -> bool:
    """Function for saving bot_id message and user_id message"""
    async with aiosqlite.connect(database_name) as db:
        await db.execute(f'CREATE TABLE IF NOT EXISTS "{user_id}" (bot_message_id INTEGER, chat_message_id INTEGER UNIQUE)')
        await db.execute(f'INSERT OR REPLACE INTO "{user_id}" (bot_message_id, chat_message_id) VALUES (?, ?)', (bot_message_id, chat_message_id))
        await db.commit()
        return True

async def get_message_id_from_bot_chat(user_id: int, chat_message_id: int) -> int:
    """Function for search message id in bot chat from user chat id and user message id. Return bot message id."""
    async with aiosqlite.connect(database_name) as db:
        async with db.execute(f'SELECT bot_message_id FROM "{user_id}" WHERE chat_message_id = ?', (chat_message_id, )) as cursor:
            row = await cursor.fetchall()
            if len(row) > 0:
                return row[-1][0]
            else:
                return None