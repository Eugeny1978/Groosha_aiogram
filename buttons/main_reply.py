import asyncio
import logging
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters import Command, CommandStart, or_f, CommandObject
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from datetime import datetime
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import config

# one_time_keyboard - есть свойство
# selective - только выборочно не всем пользователям

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()

kb = [
    [types.KeyboardButton(text="С пюрешкой")],
    [types.KeyboardButton(text="Без пюрешки")]
    ]
keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )

kb1 = [
    [types.KeyboardButton(text="С подливкой")],
    [types.KeyboardButton(text="С салатом")],
    [types.KeyboardButton(text="С капустой")]
    ]
one_time_keyboard = types.ReplyKeyboardMarkup(
    keyboard=kb1,
    resize_keyboard=True,
    input_field_placeholder="Выберите способ подачи",
    one_time_keyboard=True,
    selective=True # пока не понятно как именно задать выбор
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Как подавать котлеты?", reply_markup=keyboard)

@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message, command: CommandObject):
    example_info = "Пример: /reply_builder 20"
    if command.args is None:
        await message.answer(f"Ошибка | Сколько нужно кнопок?.\n{example_info}")
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        num = int(command.args)
    except ValueError:
        await message.answer(f"Ошибка | Неправильный формат команды.\n{example_info}")
        return
    builder = ReplyKeyboardBuilder()
    for i in range(1, num+1):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(5) # количество в одном ряду либо tuple(2, 1, 4) - можно варьировать!
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(Command("one_time_kb"))
async def reply_builder(message: types.Message):
    await message.answer("VIP Persons: Как подавать котлеты?", reply_markup=one_time_keyboard)


@dp.message(F.text.casefold() == "с пюрешкой") # casefold() == lower()
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.lower() == "без пюрешки")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно!")
@dp.message(F.text == "13") #
async def with_puree(message: types.Message):
    await message.reply("Несчастливое число!")

@dp.message(or_f(F.text.contains('10'), F.text.contains('5'))) #
async def with_puree(message: types.Message):
    await message.reply("Goog Job!", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text) #
async def with_puree(message: types.Message):
    await message.reply("Hmm...")

async def main():
    await dp.start_polling(bot) #

if __name__ == "__main__":
    asyncio.run(main())