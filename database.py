import aiosqlite
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
database_name = os.getenv('database_name')

async def init_db() -> None:
    """Function for init DataBase."""
    async with aiosqlite.connect(database_name) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS "topics" (chat_id INTEGER UNIQUE, topic_id INTEGER)')
        await db.commit()

async def save_message(user_id: int, bot_message_id: int, chat_message_id: int) -> None:
    """Function for save message_chat_id for bot_message_id."""
    async with aiosqlite.connect(database_name) as db:
        await db.execute(f'CREATE TABLE IF NOT EXISTS "{user_id}" (bot_message_id INTEGER, chat_message_id INTEGER UNIQUE)')
        await db.execute(f'INSERT OR REPLACE INTO "{user_id}" (bot_message_id, chat_message_id) VALUES (?, ?)', (bot_message_id, chat_message_id))
        await db.commit()

async def search_topic_id(chat_id: int) -> int | bool:
    """Function for search topic id from chat_id."""
    async with aiosqlite.connect(database_name) as db:
        async with db.execute('SELECT topic_id FROM "topics" WHERE chat_id = ?', (chat_id, )) as cursor:
            raw_data = await cursor.fetchone()

        return raw_data[0] if raw_data else False

async def save_topic_id(chat_id: int, topic_id: int) -> None:
    """Function for save topic id."""
    async with aiosqlite.connect(database_name) as db:
        await db.execute('INSERT INTO "topics" (chat_id, topic_id) VALUES (?, ?)', (chat_id, topic_id))
        await db.commit()

async def get_message_id_from_bot_chat(user_id: int, chat_message_id: int) -> int:
    """Function for search message id in bot chat from user chat id and user message id. Return bot message id."""
    async with aiosqlite.connect(database_name) as db:
        async with db.execute(f'SELECT bot_message_id FROM "{user_id}" WHERE chat_message_id = ?', (chat_message_id, )) as cursor:
            row = await cursor.fetchall()
            if len(row) > 0:
                return row[-1][0]
            else:
                return None

async def get_statistic() ->  tuple[int, int]:
    """Function for get statistic from database. Return count of tables and count of records"""
    async with aiosqlite.connect(database_name) as db:
        async with db.execute('SELECT name FROM sqlite_master WHERE type="table" AND name != "topics"') as cursor:
            tables = await cursor.fetchall()

        count = 0
        for table in tables:
            async with db.execute(f"SELECT COUNT(*) FROM '{table[0]}'") as cursor:
                count_raw = await cursor.fetchone()
                count += count_raw[0]

        return len(tables), count