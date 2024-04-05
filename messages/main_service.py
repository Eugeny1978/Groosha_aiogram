"""
У служебных сообщений о добавлении (new_chat_members) и выходе (left_chat_member) есть одна неприятная особенность:
они ненадёжны, т.е. они могут не создаваться вообще.
Сообщение о new_chat_members перестаёт создаваться при ~10k участников в группе,
left_chat_member - уже при 50 и менее (были случаи left_chat_member не появился и при 9 участниках.
А через полчаса там же появился при выходе другого человека).

С выходом Bot API 5.0 у разработчиков появился гораздо более надёжный способ видеть входы/выходы участников
в группах любого размера, а также в каналах. Но об этом - ОСОБЫЕ АПДЕЙТЫ
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters import Command, CommandStart, or_f, CommandObject
from aiogram.types import Message, FSInputFile, URLInputFile, BufferedInputFile
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from aiogram.utils.media_group import MediaGroupBuilder
from datetime import datetime
import os

import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()

media_dir = f"{os.path.dirname(__file__)}/media" # Целевая папка
dv_line = '-' * 60

@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        # проперти full_name берёт сразу имя И фамилию (на бывает у юзеров нет фамилии)
        await message.reply(f"Привет, {user.full_name}")



async def main():
    await dp.start_polling(bot) #

if __name__ == "__main__":
    asyncio.run(main())