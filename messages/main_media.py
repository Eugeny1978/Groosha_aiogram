import asyncio
import logging
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters import Command, CommandStart, or_f, CommandObject
from aiogram.types import Message, FSInputFile, URLInputFile, BufferedInputFile
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from datetime import datetime
import os

import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()

# бот моментально ответит пользователю той же гифкой, что была прислана
@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)

# Загрузка Файлов
@dp.message(Command('images'))
async def upload_photo(message: Message):
    # Сюда будем помещать file_id отправленных файлов, чтобы потом ими воспользоваться
    file_ids = []
    # Чтобы продемонстрировать BufferedInputFile, воспользуемся "классическим"
    # открытием файла через `open()`. Но, вообще говоря, этот способ
    # лучше всего подходит для отправки байтов из оперативной памяти
    # после проведения каких-либо манипуляций, например, редактированием через Pillow
    temp_dir = os.path.dirname(__file__)
    with open(file=temp_dir+r"/media/buffer_emulation_.jpg", mode="rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(image_from_buffer.read(), filename="image_from_buffer.jpg"),
            caption="Изображение из буфера")
        file_ids.append(result.photo[-1].file_id)
    # Отправка файла из файловой системы
    image_from_pc = FSInputFile(temp_dir+r"/media/image_from_pc.jpg")
    result = await message.answer_photo(image_from_pc, caption="Изображение из файла на компьютере")
    file_ids.append(result.photo[-1].file_id)
    # Отправка файла по ссылке
    url_adress = 'https://ae04.alicdn.com/kf/Sa780e839357844c0a90c66d8724bbf25k.jpg_640x640.jpg'
    image_from_url = URLInputFile(url_adress)
    result = await message.answer_photo(image_from_url, caption="Изображение по ссылке")
    file_ids.append(result.photo[-1].file_id)
    await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))



async def main():
    await dp.start_polling(bot) #

if __name__ == "__main__":
    asyncio.run(main())