from aiogram import Bot
from aiogram.types import BotCommand


async def set_my_default_commands(bot: Bot):
    await bot.set_my_commands(
        commands=[
            BotCommand("/start", "Welcome"),
            BotCommand("/language", "Set Language")
            ],
    )
    await bot.set_my_commands(
        commands=[
            BotCommand("/start", "Главное меню"),
            BotCommand("/language", "Выбрать язык")
            ],
        language_code='ru'
    )

