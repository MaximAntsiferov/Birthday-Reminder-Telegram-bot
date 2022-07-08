from typing import Union

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.filters import BackMenuFilter, AddNoteFilter, ChooseNotificationFilter, ApproveDataFilter, SkipFilter
from tgbot.keyboards import main_menu_button, back_or_main_keyboard, add_year_keyboard, add_notification_keyboard, \
    approving_keyboard
from tgbot.middlewares.language_middleware import _
from tgbot.misc.check_date_format import correct_date_format, correct_year_format, lower_than_current
from tgbot.misc.notification_views import long_notification
from tgbot.misc.numbers_to_months import months
from tgbot.misc.states import AddPersonStates
from tgbot.db import exist_in_db, add_person_to_db
from tgbot.scheduler import add_to_scheduler

# Хэндлер для кнопки "Добавить"
async def add_person_handler(call: CallbackQuery):
    text = _("Введите имя человека, которого хотите добавить в список дней рождений."
             "\n"
             "\nНапример: <b>Олег В.</b>")

    await call.answer(cache_time=60)
    await call.message.answer(text=text, reply_markup=main_menu_button())
    await AddPersonStates.waiting_for_name.set()


# Хэндлер для меню "Введите число и месяц рождения"
async def add_date_handler(target: Union[Message, CallbackQuery], state: FSMContext):
    text = _("Такое имя уже есть в Вашем списке.\n"
             "\n"
             "Введите, пожалуйста, уникальное имя.")

    text2 = _("Вы ввели имя: <b>{name}</b>\n"
              "\n"
              "Теперь введите число и месяц рождения.\n"
              "Например: <b>19.01</b>")

    if isinstance(target, Message):
        if await exist_in_db(name=target.text, user_id=target.from_user.id):
            await target.answer(text=text, reply_markup=main_menu_button())
        else:
            await state.update_data(name=target.text)
            await target.answer(text=text2.format(name=target.text), reply_markup=back_or_main_keyboard())
            await AddPersonStates.waiting_for_date.set()

    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        data = await state.get_data()
        name = data.get("name")
        await target.message.answer(text=text2.format(name=name), reply_markup=back_or_main_keyboard())
        await AddPersonStates.waiting_for_date.set()
    else:
        return


# Хэндлер для меню "Введите год рождения"
async def add_year_handler(target: Union[Message, CallbackQuery], state: FSMContext):
    text = _("Вы ввели имя: <b>{name}</b>\n"
             "Вы ввели дату: <b>{day} {month}</b>\n"
             "\n"
             "Теперь введите год рождения.\n"
             "Например: <b>1990</b>")

    text2 = _("Вы ввели несуществующую дату.\n"
              "\n"
              "Введите, пожалуйста, число и месяц в формате <b>DD.ММ</b>.\n"
              "Например <b>19.01</b>")

    data = await state.get_data()
    name = data.get("name")

    if isinstance(target, Message):
        if await correct_date_format(message=target.text):
            await state.update_data(day=target.text[:2], month=target.text[-2:])
            await target.answer(text=text.format(name=name, day=target.text[:2], month=months()[target.text[-2:]]),
                                reply_markup=add_year_keyboard())
            await AddPersonStates.waiting_for_year.set()
        else:
            await target.answer(text=text2, reply_markup=back_or_main_keyboard())

    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        day = data.get("day")
        month = data.get("month")
        await target.message.answer(text=text.format(name=name, day=day, month=months()[month]),
                                    reply_markup=add_year_keyboard())
        await AddPersonStates.waiting_for_year.set()

    else:
        return


# Хэндлер для меню "Выберите когда напоминать о ДР"
async def add_notification_handler(target: Union[Message, CallbackQuery], state: FSMContext):
    text = _("Вы ввели имя: <b>{name}</b>\n"
             "Вы ввели дату: <b>{day} {month}</b>\n"
             "Вы ввели год: <b>{year}</b>\n"
             "\n"
             "Теперь выберите когда напоминать Вам о Дне Рождения <b>{name}</b>:")

    text2 = _("Год рождения не может быть больше текущего года.\n"
              "\n"
              "Введите корректный год рождения.\n"
              "Например: <b>1990</b>")

    text3 = _("Не правильный формат ввода.\n"
              "\n"
              "Введите год рождения в формате <b>YYYY</b>.\n"
              "Например: <b>1990</b>")

    data = await state.get_data()
    name = data.get("name")
    day = data.get("day")
    month = data.get("month")

    if isinstance(target, Message):
        if not await correct_year_format(message=target.text):
            await target.answer(text=text3, reply_markup=add_year_keyboard())
        elif not await lower_than_current(message=target.text):
            await target.answer(text=text2, reply_markup=add_year_keyboard())
        else:
            await state.update_data(year=target.text)
            await target.answer(text=text.format(name=name, day=day, month=months()[month], year=target.text),
                                reply_markup=add_notification_keyboard())
            await AddPersonStates.waiting_for_notification.set()

    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        if target.data == "skip":
            await state.update_data(year=None)
            await target.message.answer(text=text.format(name=name, day=day, month=months()[month], year="####"),
                                        reply_markup=add_notification_keyboard())
            await AddPersonStates.waiting_for_notification.set()
        else:
            year = data.get("year")
            await target.message.answer(text=text.format(name=name, day=day, month=months()[month], year=year),
                                        reply_markup=add_notification_keyboard())
            await AddPersonStates.waiting_for_notification.set()
    else:
        return


# Хэндлер для меню "Подтвердите введенные данные"
async def check_before_add_handler(call: CallbackQuery, state: FSMContext):
    text = _("Проверьте введеные данные:\n"
             "\n"
             "Вы ввели имя: <b>{name}</b>\n"
             "Вы ввели дату: <b>{day} {month}</b>\n"
             "Вы ввели год: <b>{year}</b>\n"
             "\n"
             "Напоминать:\n"
             "<b>{notification}</b>\n"
             "\n"
             "Нажмите кнопку 'Все верно', чтобы установить ежегодное напоминание о Дне Рождения <b>{name}</b>")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name")
    day = data.get("day")
    month = data.get("month")
    year = data.get("year")
    long_note = await long_notification(call.data)
    await state.update_data(notification=call.data)
    await call.message.answer(
        text=text.format(name=name, day=day, month=months()[month], year=year, notification=long_note),
        reply_markup=approving_keyboard())
    await AddPersonStates.waiting_for_saving.set()


# Хэндлер для завершения добавления нового напоминания с записью в БД
async def adding_complete_handler(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    text = _("<b>Отлично! Напоминание добавлено!</b>")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name")
    day = data.get("day")
    month = data.get("month")
    year = data.get("year")
    notification = data.get("notification")
    print(notification)
    user_id = call.from_user.id
    bot = Bot.get_current()
    await add_person_to_db(user_id=user_id, name=name, day=day, month=month, year=year,
                           notification=notification)
    await call.message.answer(text=text, reply_markup=main_menu_button())
    await add_to_scheduler(scheduler, bot, name, day, month, year, user_id, notification)
    print(scheduler.get_jobs())
    await state.finish()


def reg_add_person_handlers(dp: Dispatcher):
    # Регистрация хэндлеров многоуровнего меню "Добавить"
    dp.register_callback_query_handler(add_person_handler, AddNoteFilter(), state="*")
    dp.register_message_handler(add_date_handler, state=AddPersonStates.waiting_for_name)
    dp.register_message_handler(add_year_handler, state=AddPersonStates.waiting_for_date)
    dp.register_message_handler(add_notification_handler, state=AddPersonStates.waiting_for_year)
    dp.register_callback_query_handler(add_notification_handler, SkipFilter(), state=AddPersonStates.waiting_for_year)
    dp.register_callback_query_handler(check_before_add_handler, ChooseNotificationFilter(),
                                       state=AddPersonStates.waiting_for_notification)
    dp.register_callback_query_handler(adding_complete_handler, ApproveDataFilter(),
                                       state=AddPersonStates.waiting_for_saving)

    # Регистрация хэндлеров кнопки "Назад" в ветке "Добавить"
    dp.register_callback_query_handler(add_person_handler, BackMenuFilter(), state=AddPersonStates.waiting_for_date)
    dp.register_callback_query_handler(add_date_handler, BackMenuFilter(), state=AddPersonStates.waiting_for_year)
    dp.register_callback_query_handler(add_year_handler, BackMenuFilter(), state=AddPersonStates.waiting_for_notification)
    dp.register_callback_query_handler(add_notification_handler, BackMenuFilter(),
                                       state=AddPersonStates.waiting_for_saving)
