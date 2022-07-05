import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.add_person_handlers import reg_add_person_handlers
from handlers.basic_handlers import reg_basic_handlers
from handlers.inside_the_list.del_person_handlers import reg_del_person_handlers
from handlers.inside_the_list.inside_editing.edit_date_handlers import reg_edit_date_handlers
from handlers.inside_the_list.inside_editing.edit_name_handlers import reg_edit_name_handlers
from handlers.inside_the_list.inside_editing.edit_notification_handlers import reg_edit_notification_handlers
from handlers.inside_the_list.edit_person_handlers import reg_edit_person_handlers
from handlers.look_at_list_handler import reg_look_at_list_handler
from middlewares.language_middleware import reg_language_middleware
from middlewares.scheduler_middleware import reg_scheduler_middleware
from scheduler import tasks_on_startup
from tgbot.config import BOT_TOKEN
from tgbot.filters import register_all_filters
from db import create_tables
from commands import set_my_default_commands

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, scheduler):
    reg_language_middleware(dp)
    reg_scheduler_middleware(dp, scheduler)


def register_all_handlers(dp):
    reg_basic_handlers(dp)
    reg_add_person_handlers(dp)
    reg_look_at_list_handler(dp)
    reg_del_person_handlers(dp)
    reg_edit_person_handlers(dp)
    reg_edit_name_handlers(dp)
    reg_edit_date_handlers(dp)
    reg_edit_notification_handlers(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler()

    register_all_filters(dp)
    register_all_handlers(dp)
    register_all_middlewares(dp, scheduler)

    await set_my_default_commands(bot)
    await create_tables()
    scheduler.start()
    await tasks_on_startup(scheduler, bot)


    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
