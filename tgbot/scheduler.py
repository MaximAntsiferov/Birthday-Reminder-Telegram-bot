from datetime import date, timedelta
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.db import connection_to_db, close_connection
from tgbot.middlewares.language_middleware import _


async def tasks_on_startup(scheduler: AsyncIOScheduler, bot: Bot):
    connection = await connection_to_db()
    values = await connection.fetch(f"SELECT * FROM birthdays")
    await close_connection(connection)
    for data in values:
        user_id = data["user_id"]
        name = data["name"]
        year = data["year"]
        month = data["month"]
        day = data["day"]
        notification = data["notification"]
        await add_to_scheduler(scheduler, bot, name, day, month, year, user_id, notification)


async def add_to_scheduler(scheduler: AsyncIOScheduler, bot: Bot, name: str, day: str, month: str, year: str,
                           user_id: int, notification: str):
    day = int(day)
    month = int(month)

    if notification == "on_date":
        scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          args=[bot, name, year, user_id], name=f"onday_{user_id}_{name}")
    elif notification == "three_days_before":
        day, month = await calculate_3days_before(day=day, month=month)
        scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          args=[bot, name, year, user_id], name=f"before_{user_id}_{name}")
    elif notification == "both_variants":
        scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          args=[bot, name, year, user_id], name=f"onday_{user_id}_{name}")
        day, month = await calculate_3days_before(day=day, month=month)
        scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          args=[bot, name, year, user_id], name=f"before_{user_id}_{name}")
    else:
        return


async def calculate_3days_before(day: int, month: int):
    if day - 3 <= 0:
        calculated_date = date(date.today().year, month, day) - timedelta(days=3)
        day = calculated_date.day
        month = calculated_date.month
    return day, month


async def add_onday_reminder(bot: Bot, name: str, year: int, user_id: int):
    text = _("Сегодня <b>{name}</b> отмечает свой <b>{age}{ending}</b> День Рождения!\n\n"
             "Не забывай поздравлять важных тебе людей")

    ending = _("-й") if year is not None else _("")
    age = date.today().year - year
    await bot.send_message(text=text.format(name=name, age=age, ending=ending), chat_id=user_id)


async def add_3daysbefore_reminder(bot: Bot, name: str, year: int, user_id: int):
    text = _("Через 3 дня <b>{name}</b> будет отмечать свой <b>{age}{ending}</b> День Рождения!\n\n"
             "Не забывай поздравлять важных тебе людей")

    ending = _("-й") if year is not None else _("")
    birthday = date.today() + timedelta(days=3)
    age = birthday.year - int(year)
    await bot.send_message(text=text.format(name=name, age=age, ending=ending), chat_id=user_id)


async def del_from_scheduler(scheduler: AsyncIOScheduler, onday_id: str, before_id: str):
    if onday_id is not None:
        scheduler.remove_job(job_id=onday_id)
    if before_id is not None:
        scheduler.remove_job(job_id=before_id)
    return


async def get_id_by_name(scheduler: AsyncIOScheduler, user_id: int, name: str):
    list_of_all_jobs = scheduler.get_jobs()
    onday_id = None
    before_id = None
    for job in list_of_all_jobs:
        if job.name == f"onday_{user_id}_{name}":
            onday_id = job.id
        if job.name == f"before_{user_id}_{name}":
            before_id = job.id
    return onday_id, before_id


async def modify_name(scheduler: AsyncIOScheduler, user_id: int, new_name: str, onday_id: str, before_id: str):
    if onday_id is not None:
        scheduler.modify_job(job_id=onday_id, name=f"onday_{user_id}_{new_name}")
    if before_id is not None:
        scheduler.modify_job(job_id=before_id, name=f"before_{user_id}_{new_name}")
    return


async def modify_date(scheduler: AsyncIOScheduler, new_day: str, new_month: str, onday_id: str, before_id: str):
    new_day = int(new_day)
    new_month = int(new_month)
    if onday_id is not None:
        scheduler.reschedule_job(job_id=onday_id, trigger="cron", month=new_month, day=new_day, hour=9, minute=0)
    if before_id is not None:
        new_day, new_month = await calculate_3days_before(day=new_day, month=new_month)
        scheduler.reschedule_job(job_id=before_id, trigger="cron", month=new_month, day=new_day, hour=9, minute=0)


async def modify_notification(scheduler: AsyncIOScheduler, bot: Bot, notification: str, user_id: str, name: str,
                              year: int, month: int, day: int, onday_id: str, before_id: str):

    if notification == "on_date":
        if onday_id is None:
            scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              args=[bot, name, year, user_id], name=f"onday_{user_id}_{name}")
        if before_id is not None:
            scheduler.remove_job(job_id=before_id)

    elif notification == "three_days_before":
        if before_id is None:
            day, month = await calculate_3days_before(day=day, month=month)
            scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              args=[bot, name, year, user_id], name=f"before_{user_id}_{name}")
        if onday_id is not None:
            scheduler.remove_job(job_id=onday_id)

    elif notification == "both_variants":
        if onday_id is None:
            scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              args=[bot, name, year, user_id], name=f"onday_{user_id}_{name}")
        if before_id is None:
            day, month = await calculate_3days_before(day=day, month=month)
            scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              args=[bot, name, year, user_id], name=f"before_{user_id}_{name}")
