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
        await db.execute(f'CREATE TABLE IF NOT EXISTS "{user_id}" (bot_message_id INTEGER, chat_message_id INTEGER)')
        await db.execute(f'INSERT INTO "{user_id}" (bot_message_id, chat_message_id) VALUES (?, ?)', (bot_message_id, chat_message_id))
        await db.commit()