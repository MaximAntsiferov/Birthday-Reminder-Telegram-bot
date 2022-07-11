from datetime import date, timedelta
from typing import Optional

from aiogram import Bot
from apscheduler_di import ContextSchedulerDecorator

from tgbot.db import connection_to_db, close_connection
from tgbot.middlewares.language_middleware import _


# Добавляем все ранее созданные задания из БД в планировщик, если список заданий пуст
async def tasks_on_startup(scheduler: ContextSchedulerDecorator):
    jobs = scheduler.get_jobs()
    if len(jobs) == 0:
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
    else:
        return


# Добавляем новые задания в планировщик
async def add_to_scheduler(scheduler: ContextSchedulerDecorator, name: str, day: str, month: str, year: Optional[str],
                           user_id: int, notification: str):
    day = int(day)
    month = int(month)
    year = int(year) if year is not None else None

    if notification == "on_date":
        scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                          name=f"onday_{user_id}_{name}")
    elif notification == "three_days_before":
        day, month = await calculate_3days_before(day=day, month=month)
        scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                          name=f"before_{user_id}_{name}")
    elif notification == "both_variants":
        scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                          name=f"onday_{user_id}_{name}")
        day, month = await calculate_3days_before(day=day, month=month)
        scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                          kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                          name=f"before_{user_id}_{name}")
    else:
        return


# Вычисляем какой день и месяц будут за 3 дня до Дня рождения
async def calculate_3days_before(day: int, month: int):
    if day - 3 <= 0:
        calculated_date = date(date.today().year, month, day) - timedelta(days=3)
        day = calculated_date.day
        month = calculated_date.month
    else:
        day = day - 3
    return day, month


# Вычисляем сколько лет исполнится человеку в ближайший День рождения
async def calculate_coming_age(day: int, month: int, year: int, shift: int) -> int:
    ref_point = date.today() + timedelta(days=shift)
    person_years = ref_point.year - year
    person_months = ref_point.month - month
    person_days = ref_point.day - day
    if person_months < 0:
        age = person_years
    elif person_months == 0 and person_days < 0:
        age = person_years
    else:
        age = person_years + 1
    return age


# Напоминание срабатывающее в День рождения
async def add_onday_reminder(bot: Bot, name: str, day: int, month: int, year: Optional[int], user_id: int):
    text = _("Сегодня <b>{name}</b> отмечает свой <b>{age}{ending}</b> День Рождения!\n\n"
             "Не забудь отправить поздравление!")

    if year is None:
        ending = ""
        age = ""
    else:
        ending = _("-й")
        age = await calculate_coming_age(day=day, month=month, year=year, shift=0)
    await bot.send_message(text=text.format(name=name, age=age, ending=ending), chat_id=user_id)


# Напоминание срабатывающее за 3 дня до Дня рождения
async def add_3daysbefore_reminder(bot: Bot, name: str, day: int, month: int, year: Optional[int], user_id: int):
    text = _("Через 3 дня <b>{name}</b> будет отмечать свой <b>{age}{ending}</b> День Рождения!\n\n"
             "Не забудь приготовить подарок!")

    if year is None:
        ending = ""
        age = ""
    else:
        ending = _("-й")
        age = await calculate_coming_age(day=day, month=month, year=year, shift=3)

    await bot.send_message(text=text.format(name=name, age=age, ending=ending), chat_id=user_id)


# Удаляем задание из планировщика
async def del_from_scheduler(scheduler: ContextSchedulerDecorator, onday_id: Optional[str], before_id: Optional[str]):
    if onday_id is not None:
        scheduler.remove_job(job_id=onday_id)
    if before_id is not None:
        scheduler.remove_job(job_id=before_id)
    return


# Получаем ID задания в планировщике по имени задания
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


# Изменяем имя задания в планировщике
async def modify_name(scheduler: ContextSchedulerDecorator, user_id: int, new_name: str, onday_id: Optional[str],
                      before_id: Optional[str]):
    if onday_id is not None:
        scheduler.modify_job(job_id=onday_id, name=f"onday_{user_id}_{new_name}")
    if before_id is not None:
        scheduler.modify_job(job_id=before_id, name=f"before_{user_id}_{new_name}")
    return


# Изменяем дату срабатывания задания в планировщике
async def modify_date(scheduler: ContextSchedulerDecorator, new_day: str, new_month: str, onday_id: Optional[str],
                      before_id: Optional[str]):
    new_day = int(new_day)
    new_month = int(new_month)
    if onday_id is not None:
        scheduler.reschedule_job(job_id=onday_id, trigger="cron", month=new_month, day=new_day, hour=9, minute=0)
    if before_id is not None:
        new_day, new_month = await calculate_3days_before(day=new_day, month=new_month)
        scheduler.reschedule_job(job_id=before_id, trigger="cron", month=new_month, day=new_day, hour=9, minute=0)


# Изменяем тип напоминания задания в планировщике
async def modify_notification(scheduler: ContextSchedulerDecorator, notification: str, user_id: int, name: str,
                              year: Optional[int], month: int, day: int, onday_id: Optional[str],
                              before_id: Optional[str]):
    if notification == "on_date":
        if onday_id is None:
            scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                              name=f"onday_{user_id}_{name}")
        if before_id is not None:
            scheduler.remove_job(job_id=before_id)

    elif notification == "three_days_before":
        if before_id is None:
            day, month = await calculate_3days_before(day=day, month=month)
            scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                              name=f"before_{user_id}_{name}")
        if onday_id is not None:
            scheduler.remove_job(job_id=onday_id)

    elif notification == "both_variants":
        if onday_id is None:
            scheduler.add_job(add_onday_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                              name=f"onday_{user_id}_{name}")
        if before_id is None:
            day, month = await calculate_3days_before(day=day, month=month)
            scheduler.add_job(add_3daysbefore_reminder, "cron", month=month, day=day, hour=9, minute=0,
                              kwargs={"name": name, "day": day, "month": month, "year": year, "user_id": user_id},
                              name=f"before_{user_id}_{name}")
