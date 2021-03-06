import asyncio
import logging
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from tgbot.commands import set_my_default_commands
from tgbot.config import BOT_TOKEN, USE_REDIS
from tgbot.db import create_tables
from tgbot.filters import register_all_filters
from tgbot.handlers.add_person_handlers import reg_add_person_handlers
from tgbot.handlers.basic_handlers import reg_basic_handlers
from tgbot.handlers.inside_the_list.del_person_handlers import reg_del_person_handlers
from tgbot.handlers.inside_the_list.edit_person_handlers import reg_edit_person_handlers
from tgbot.handlers.inside_the_list.inside_editing.edit_date_handlers import reg_edit_date_handlers
from tgbot.handlers.inside_the_list.inside_editing.edit_name_handlers import reg_edit_name_handlers
from tgbot.handlers.inside_the_list.inside_editing.edit_notification_handlers import reg_edit_notification_handlers
from tgbot.handlers.look_at_list_handler import reg_look_at_list_handler
from tgbot.middlewares.language_middleware import reg_language_middleware
from tgbot.middlewares.scheduler_middleware import reg_scheduler_middleware
from tgbot.scheduler import tasks_on_startup

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

    storage = RedisStorage2() if USE_REDIS else MemoryStorage()
    bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    job_stores: Dict[str, RedisJobStore] = {
        "default": RedisJobStore(
            jobs_key="birthdays_jobs", run_times_key="birthdays_run_times"
        )
    }

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))
    scheduler.ctx.add_instance(bot, Bot)

    register_all_filters(dp)
    register_all_handlers(dp)
    register_all_middlewares(dp, scheduler)

    await set_my_default_commands(bot)
    await create_tables()
    scheduler.start()
    await tasks_on_startup(scheduler)


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
