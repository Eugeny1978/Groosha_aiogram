import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters import Command, CommandStart, or_f, CommandObject
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from datetime import datetime

import config

def get_msg(text: str):
    return text.split('_')[-1]


logging.basicConfig(level=logging.INFO)
# bot = Bot(token=config.TOKEN)
bot = Bot(token=config.TOKEN, parse_mode="HTML") # для всего бота метод форматирования
dp = Dispatcher()

# Если не указать фильтр F.text, то хэндлер сработает даже на картинку с подписью /test
@dp.message(F.text, Command("test1"))
async def any_message(message: Message):
    user = message.from_user.first_name
    await message.answer(f"Hello, <b>{user}</b>! | HTML", parse_mode=ParseMode.HTML)
    # MARKDOWN 1я версия - урезанная
    # Также обрати внимание на необходимость экранирования (\) многих символов
    await message.answer(f"Hello, *{user}*\! \| MARKDOWN\_V2", parse_mode=ParseMode.MARKDOWN_V2)

@dp.message(F.text, Command("test2"))
async def any_message(message: Message):
    user = message.from_user.first_name
    await message.answer("Сообщение с <u>HTML-разметкой</u>")
    await message.answer("Сообщение без <s>какой-либо разметки</s>", parse_mode=None)

# Недостаток текст содержащий симолы < > не будет выведен тк будет ожидать полного тега
@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(f"Hello, <b>{message.from_user.full_name}</b>") # , parse_mode=ParseMode.HTML

# 1й вариант преодоления
@dp.message(Command("hello1"))
async def cmd_hello1(message: Message):
    await message.answer(f"Hello, {html.bold(html.quote(message.from_user.full_name))}")

# 2й вариант преодоления БОЛЕЕ ПРОДВИНУТОЕ
# **content.as_kwargs() вернёт аргументы text, entities, parse_mode и подставит их в вызов answer().
# content.as_html() можно и так
@dp.message(Command("hello2"))
async def cmd_hello2(message: Message):
    content = Text("Hello, ", Bold(message.from_user.full_name))
    await message.answer(**content.as_kwargs())


# проверю 1й способ:
@dp.message(F.text.lower().startswith("/hello1_"))
async def check_hello1(message: Message):
    await message.answer(f"Hello, {html.bold(html.quote(get_msg(message.text)))}")

# проверю 2й способ:
@dp.message(F.text.casefold().startswith("/hello2_")) # casefold() - аналог lower()
async def check_hello2(message: Message):
    content = Text("Hello, ", Bold(get_msg(message.text)))
    await message.answer(**content.as_kwargs())
    await message.answer(content.as_html()) # альтернативно строке выше

@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    content = as_list(
        as_marked_section(
            Bold("Success:"),
            "Test 1",
            "Test 3",
            "Test 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed:"),
            "Test 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total", 4),
            as_key_value("Success", 3),
            as_key_value("Failed", 1),
            marker="  ",
        ),
        HashTag("#test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())
# Работа с message.entities - Телеграмм предобрабатывает собщения пользователей
# и есть возможность извлекать некоторые типы данных, не используя регулярные выражения:
# [MessageEntity(type='url', offset=50, length=9, url=None, user=None, language=None, custom_emoji_id=None),
#  MessageEntity(type='email', offset=88, length=13, url=None, user=None, language=None, custom_emoji_id=None),
#  MessageEntity(type='phone_number', offset=226, length=16, url=None, user=None, language=None, custom_emoji_id=None)]
# Пример запроса:
# Привет, бот! Вот твои 🔑 учетные данные с сайта yandex.ru:
# Зайти можешь на почту 📧 bot@yandex.ru.
# Твой пароль: Super34к56л234кеЕ67.
# pass: 111, # password: 222, # code: 333.
# Будут вопросы - звони мне по телефону 📱: +7-911-555-66-77
# Мой ник Robot555
# Только пожалуйста не ошибись!
@dp.message(or_f(F.text.contains('🔑'), F.text.contains('📧'), F.text.contains('📱')))
async def extract_data(message: Message):
    dataR = {
        "url": "<N/A>",
        "email": "<N/A>",
        'phone_number': "<N/A>",
        "code": "<N/A>"
    }
    dataW = dataR.copy()
    entities = message.entities or []
    print(entities)
    for item in entities:
        await message.answer(f'Есть поле: "{item.type}"')
        if item.type in dataR.keys():
            # Правильно
            dataR[item.type] = item.extract_from(message.text)
        if item.type in dataW.keys():
            # Неправильно
            dataW[item.type] = message.text[item.offset : item.offset+item.length]
    for data in (dataR, dataW):
        await message.reply(
            f"{'Правильно' if data == dataR else 'НЕправильно'} | Вот что я нашёл:\n"
            f"URL: {html.quote(data['url'])}\n"
            f"E-mail: {html.quote(data['email'])}\n"
            f"Телефон: {html.quote(data['phone_number'])}\n"
            f"Пароль: {html.quote(data['code'])}" # 2024-04-03 telegramm не распознает тип code (пароль)
        )
# Команда с параметрами
@dp.message(Command("set_timer"))
async def cmd_settimer(message: Message, command: CommandObject):
    # Если не переданы никакие аргументы, то command.args будет None
    example_info = "Пример: /settimer (time) (message)"
    if command.args is None:
        await message.answer(f"Ошибка | Не переданы аргументы.\n{example_info}")
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(f"Ошибка | Неправильный формат команды.\n{example_info}")
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )
# Кастомные префиксы для команд
@dp.message(Command("custom", prefix="%!/"))
async def cmd_custom1(message: Message):
    await message.answer('Вижу команду "custom1" c этими префиксами: % ! /')


# ДИПЛИНКИ к команде старт
# можно сформировать ссылку вида t.me/bot?start=xxx # и пре переходе по такой ссылке пользователю
# покажут кнопку «Начать», при нажатии которой бот получит сообщение /start xxx.
# Может использоваться для кучи разных вещей: шорткаты для активации различных команд, реферальная система, быстрая конфигурация бота и т.д..

#/start help
# t.me/besedin_pizza_bot?start=help
@dp.message(Command("help"))
@dp.message(CommandStart(deep_link=True, magic=F.args == "help"))
async def cmd_start_help(message: Message):
    await message.answer("Это сообщение со справкой")
    await message.answer('НО сначала кинем кости:')
    await message.answer_dice('🎲')
#/start book_587
# t.me/besedin_pizza_bot?start=book_587
@dp.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'book_(\d+)'))))
async def cmd_start_book(message: Message, command: CommandObject):
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")
    await message.answer('НО сначала кинем шар:')
    await message.answer_dice('🎳')

# Тонкости форматирования текста
@dp.message(F.text)
async def echo_with_time(message: Message):
    time_now = datetime.now().strftime('%H:%M')
    underline_time = html.underline(f'Создано в {time_now}')
    await message.answer(f"{message.text}\n{underline_time}") # вернет НЕотформатированный текст
    await message.answer(f"{message.html_text}\n{underline_time}") # вернет отформатированный текст
    # await message.answer(f"{message.mk_text}\n{underline_time}") # если кодировка маркдаун


async def main():
    await dp.start_polling(bot) #

if __name__ == "__main__":
    asyncio.run(main())