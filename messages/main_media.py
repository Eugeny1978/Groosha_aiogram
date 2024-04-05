import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters import Command, CommandStart, or_f, CommandObject
from aiogram.types import Message, FSInputFile, URLInputFile, BufferedInputFile
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.markdown import hide_link

import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()

media_dir = f"{os.path.dirname(__file__)}/media" # Целевая папка
dv_line = '-' * 60
div_line = '\n' + dv_line + '\n'


# бот моментально ответит пользователю той же гифкой, что была прислана
@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)

# Загрузка Файлов
# для Windows пути - сделаны абсолютными
# message.photo[-1] - фото всегда приходит в нескольких экзеплярах. последний - самый большой
@dp.message(Command('images'))
async def upload_photo(message: Message):
    # Сюда будем помещать file_id отправленных файлов, чтобы потом ими воспользоваться
    file_ids = []
    # Чтобы продемонстрировать BufferedInputFile, воспользуемся "классическим" открытием файла через `open()`.
    # этот способ лучше всего подходит для отправки байтов из оперативной памяти
    # после проведения каких-либо манипуляций, например, редактированием через Pillow
    with open(file=f"{media_dir}/buffer_emulation_.jpg", mode="rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(image_from_buffer.read(), filename="image_from_buffer.jpg"),
            caption="Изображение из буфера")
        file_ids.append(result.photo[-1].file_id)
    # Отправка файла из файловой системы
    image_from_pc = FSInputFile(f"{media_dir}/image_from_pc.jpg")
    result = await message.answer_photo(image_from_pc, caption="Изображение из файла на компьютере")
    file_ids.append(result.photo[-1].file_id)
    # Отправка файла по ссылке
    url_adress = 'https://ae04.alicdn.com/kf/Sa780e839357844c0a90c66d8724bbf25k.jpg_640x640.jpg'
    image_from_url = URLInputFile(url_adress)
    result = await message.answer_photo(image_from_url, caption="Изображение по ссылке")
    file_ids.append(result.photo[-1].file_id)
    content = as_list(Bold("Отправленные файлы:"), div_line.join(file_ids))
    # await message.answer(f"Отправленные файлы:{div_line}" + div_line.join(file_ids))
    await message.answer(content.as_html())

# Скачивание файлов
# для Windows пути - сделаны абсолютными
@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    # print(message.photo[-1]) # 5 полей: file_id='AgA...' file_unique_id='AQA...' width=482 height=258 file_size=21890
    file_name = f"{message.photo[-1].file_id}.jpg"
    await bot.download(message.photo[-1], destination=(media_dir + file_name))
    # await message.answer(f"Фото загружено в \n{media_dir}.{div_line}Имя файла: \n{file_name}")
    content = as_list("Фото загружено в:", media_dir, dv_line, "Имя файла:", file_name)
    await message.answer(content.as_html())

@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    file_name = f"{message.sticker.file_id}.jpg"
    await bot.download(message.sticker, destination=(media_dir + file_name))
    # await message.answer(f"Стикер загружен в {media_dir}.{div_line}Имя файла: {file_name}")
    content = as_list("Стикер загружен в:", media_dir, dv_line, "Имя файла:", file_name)
    await message.answer(content.as_html())

# АЛЬБОМЫ
@dp.message(Command("album"))
async def cmd_album(message: Message):
    album_builder = MediaGroupBuilder(caption="Общая подпись для будущего альбома")
    album_builder.add(
        type="photo",
        media=FSInputFile(f"{media_dir}/image_from_pc.jpg")
        # caption="Подпись к конкретному медиа"
    )
    # Если мы сразу знаем тип, то вместо общего add можно сразу вызывать add_<тип>
    # Для ссылок или file_id достаточно сразу указать значение
    album_builder.add_photo(media="https://ae04.alicdn.com/kf/Sa780e839357844c0a90c66d8724bbf25k.jpg_640x640.jpg")
    album_builder.add_photo(media="AgACAgIAAxkBAAIHPGYPpdhPqZMlm2WV-gABwQFeY67d5QACVdsxG1C2eUg8z0wUkTnawwEAAwIAA3gAAzQE") # "<ваш file_id>"
    # Не забудьте вызвать build()
    await message.answer_media_group(media=album_builder.build())


# Прячем ссылку в тексте
# Подписи к медиафайлам = 1024 символа против 4096 у обычного текстового, а вставлять внизу ссылку на медиа — выглядит некрасиво.
# Подход со «скрытыми ссылками» в HTML-разметке.
# Разработчики aiogram для этого сделали специальный вспомогательный метод hide_link().
@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документация Telegram: существует ⚙️\n"
        f"Пользователи: не читают документацию 🧻\n"
        f"Разработчики:"
    )


async def main():
    await dp.start_polling(bot) #

if __name__ == "__main__":
    asyncio.run(main())