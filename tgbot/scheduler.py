from datetime import date, timedelta
from typing import Optional

from aiogram import Bot
from apscheduler_di import ContextSchedulerDecorator

from tgbot.db import connection_to_db, close_connection
from tgbot.middlewares.language_middleware import _


# Добавляем все ранее созданные задания из БД в планировщик
async def tasks_on_startup(scheduler: ContextSchedulerDecorator):
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
        await add_to_scheduler(scheduler=scheduler, name=name, day=day, month=month, year=year,
                               user_id=user_id, notification=notification)


async def add_to_scheduler(scheduler: ContextSchedulerDecorator, name: str, day: str, month: str, year: Optional[str],
                           user_id: int, notification: str):
    day = int(day)
    month = int(month)
    year = int(year) if year is not None else None

    if notification == "on_date":
        scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "year": year, "user_id": user_id}, name=f"onday_{user_id}_{name}")
    elif notification == "three_days_before":
        day, month = await calculate_3days_before(day=day, month=month)
        scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "year": year, "user_id": user_id}, name=f"before_{user_id}_{name}")
    elif notification == "both_variants":
        scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "year": year, "user_id": user_id}, name=f"onday_{user_id}_{name}")
        day, month = await calculate_3days_before(day=day, month=month)
        scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "year": year, "user_id": user_id}, name=f"before_{user_id}_{name}")
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
             "Не забудь отправить поздравление!")

    if year is None:
        ending = ""
        age = ""
    else:
        ending = _("-й")
        age = date.today().year - year
    await bot.send_message(text=text.format(name=name, age=age, ending=ending), chat_id=user_id)


async def add_3daysbefore_reminder(bot: Bot, name: str, year: int, user_id: int):
    text = _("Через 3 дня <b>{name}</b> будет отмечать свой <b>{age}{ending}</b> День Рождения!\n\n"
             "Не забудь приготовить подарок!")

    if year is None:
        ending = ""
        age = ""
    else:
        ending = _("-й")
        birthday = date.today() + timedelta(days=3)
        age = birthday.year - int(year)
    await bot.send_message(text=text.format(name=name, age=age, ending=ending), chat_id=user_id)


async def del_from_scheduler(scheduler: ContextSchedulerDecorator, onday_id: str, before_id: str):
    if onday_id is not None:
        scheduler.remove_job(job_id=onday_id)
    if before_id is not None:
        scheduler.remove_job(job_id=before_id)
    return


async def get_id_by_name(scheduler: ContextSchedulerDecorator, user_id: int, name: str):
    list_of_all_jobs = scheduler.get_jobs()
    onday_id = None
    before_id = None
    for job in list_of_all_jobs:
        if job.name == f"onday_{user_id}_{name}":
            onday_id = job.id
        if job.name == f"before_{user_id}_{name}":
            before_id = job.id
    return onday_id, before_id


async def modify_name(scheduler: ContextSchedulerDecorator, user_id: int, new_name: str, onday_id: str, before_id: str):
    if onday_id is not None:
        scheduler.modify_job(job_id=onday_id, name=f"onday_{user_id}_{new_name}")
    if before_id is not None:
        scheduler.modify_job(job_id=before_id, name=f"before_{user_id}_{new_name}")
    return


async def modify_date(scheduler: ContextSchedulerDecorator, new_day: str, new_month: str, onday_id: str, before_id: str):
    new_day = int(new_day)
    new_month = int(new_month)
    if onday_id is not None:
        scheduler.reschedule_job(job_id=onday_id, trigger="cron", month=new_month, day=new_day, hour=9, minute=0)
    if before_id is not None:
        new_day, new_month = await calculate_3days_before(day=new_day, month=new_month)
        scheduler.reschedule_job(job_id=before_id, trigger="cron", month=new_month, day=new_day, hour=9, minute=0)


async def modify_notification(scheduler: ContextSchedulerDecorator, notification: str, user_id: int, name: str,
                              year: Optional[int], month: int, day: int, onday_id: str, before_id: str):

    if notification == "on_date":
        if onday_id is None:
            scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "year": year, "user_id": user_id}, name=f"onday_{user_id}_{name}")
        if before_id is not None:
            scheduler.remove_job(job_id=before_id)

    elif notification == "three_days_before":
        if before_id is None:
            day, month = await calculate_3days_before(day=day, month=month)
            scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "year": year, "user_id": user_id}, name=f"before_{user_id}_{name}")
        if onday_id is not None:
            scheduler.remove_job(job_id=onday_id)

    elif notification == "both_variants":
        if onday_id is None:
            scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "year": year, "user_id": user_id}, name=f"onday_{user_id}_{name}")
        if before_id is None:
            day, month = await calculate_3days_before(day=day, month=month)
            scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "year": year, "user_id": user_id}, name=f"before_{user_id}_{name}")
