import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandStart
from datetime import datetime

# не забудьте про импорт | либо можно передать избражение эмодзи прямо в код см ниже
from aiogram.enums.dice_emoji import DiceEmoji

import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.TOKEN)
# Диспетчер
dp = Dispatcher()
# Передача Доп. параметров (именованных)
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# Хэндлер на команду /start
@dp.message(CommandStart()) # Command("start")
async def cmd_start(message: types.Message):
    await message.answer(f"Hello, {message.from_user.username}!")

# Хэндлер на команду /test1
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

# Хэндлер на команду /test2
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")

@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")

# Всегда есть возможность пробросить в хендлер экземляр БОТА
# Напрмер если хотим отправить сообщение или другиие данные не в текущий чат
@dp.message(Command("dice2"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_message(chat_id=config.GROUP_id, text='Бросаю кубик:')
    await bot.send_dice(chat_id=config.GROUP_id, emoji=DiceEmoji.DICE)

@dp.message(Command("dart"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_message(chat_id=config.GROUP_id, text='Бросаю дротик:')
    await bot.send_dice(chat_id=config.GROUP_id, emoji=DiceEmoji.DART)

@dp.message(Command("basketball"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_message(chat_id=config.GROUP_id, text='Кидаю мяч:')
    await bot.send_dice(chat_id=config.GROUP_id, emoji=DiceEmoji.BASKETBALL)

@dp.message(Command("football"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_message(chat_id=config.GROUP_id, text='Кидаю мяч:')
    await bot.send_dice(chat_id=config.GROUP_id, emoji=DiceEmoji.FOOTBALL)

@dp.message(Command("bowling"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_message(chat_id=config.GROUP_id, text='Кидаю шар:')
    await bot.send_dice(chat_id=config.GROUP_id, emoji=DiceEmoji.BOWLING)

@dp.message(Command("slot"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_message(chat_id=config.GROUP_id, text='Кручу однорукий бандит:')
    await bot.send_dice(chat_id=config.GROUP_id, emoji=DiceEmoji.SLOT_MACHINE)

@dp.message(F.text.lower().startswith("/add_to_list_"))
async def cmd_add_to_list(message: types.Message, mylist: list[int|str]):
    elem = message.text.split('_')[-1]
    if elem:
        if elem.isdigit(): elem = int(elem)
        mylist.append(elem)
        await message.answer(f"В список Добавлено: {elem}")
    else:
        await message.answer(f"Вы не указали ЧТО необходимо добавить в список!")

@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int|str]):
    await message.answer(f"Ваш список: {mylist}")


@dp.message(Command("start_info"))
async def cmd_info(message: types.Message, started_at: str):
    await message.answer(f"Бот запущен {started_at}")

# DICE = "🎲"
# DART = "🎯"
# BASKETBALL = "🏀"
# FOOTBALL = "⚽"
# SLOT_MACHINE = "🎰"
# BOWLING = "🎳"


# Запуск процесса поллинга новых апдейтов
async def main():

    # пример регистрации хендлера не через декоратор а методом
    dp.message.register(cmd_test2, Command('test2'))

    # Поллинг (ловит наличие апдейтов)
    await dp.start_polling(bot, mylist=[1,2]) # mylist - это необязательный доп параметр. чтобы можно было изменять объект должен быть изменяемым

if __name__ == "__main__":
    asyncio.run(main())