from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.db import update_date_in_db
from tgbot.filters import BackMenuFilter, EditDateFilter, ApproveDataFilter, SkipFilter
from tgbot.keyboards import back_or_main_keyboard, add_year_keyboard, approving_keyboard, after_changes_keyboard
from tgbot.misc.check_date_format import correct_date_format, correct_year_format, lower_than_current
from tgbot.misc.numbers_to_months import months
from tgbot.misc.states import EditDateStates, EditPersonStates
from tgbot.middlewares.language_middleware import _
from tgbot.scheduler import get_id_by_name, modify_date

# Хэндлер для меню "Изменить дату"
async def edit_date_handler(call: CallbackQuery):
    text = _("Введите новые число и месяц.\n"
             "Например: <b>19.01</b>")

    await call.answer(cache_time=60)
    await call.message.answer(text=text, reply_markup=back_or_main_keyboard())
    await EditDateStates.waiting_for_day_month_instead.set()


# Хэндлер для меню "Изменить год"
async def edit_year_handler(target: Message | CallbackQuery, state: FSMContext):
    text = _("Вы ввели новую дату: <b>{new_day} {new_month}</b>\n"
             "\n"
             "Теперь введите новый год рождения.\n"
             "Например: <b>1990</b>")
    text2 = _("Вы ввели несуществующую дату.\n"
              "Введите пожалуйста число и месяц в формате <b>дд.мм</b>.\n"
              "Например <b>19.01</b>")

    if isinstance(target, Message):
        if await correct_date_format(message=target.text):
            new_day = target.text[:2]
            new_month = target.text[-2:]
            await state.update_data(new_day=new_day, new_month=new_month)
            await target.answer(text=text.format(new_day=new_day, new_month=months()[new_month]),
                                reply_markup=add_year_keyboard())
            await EditDateStates.waiting_for_year_instead.set()
        else:
            await target.answer(text=text2, reply_markup=back_or_main_keyboard())

    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        data = await state.get_data()
        new_day = data.get("new_day")
        new_month = data.get("new_month")
        await target.message.answer(text=text.format(new_day=new_day, new_month=months()[new_month]),
                                    reply_markup=add_year_keyboard())
        await EditDateStates.waiting_for_year_instead.set()
    else:
        return


# Хэндлер для меню "Подтвердить новую дату"
async def check_before_save_date_handler(target: Message | CallbackQuery, state: FSMContext):
    text = _(
        "Вы действительно хотите изменить дату рождения <b>{name}</b> на <b>{new_day}.{new_month}.{new_year}</b>?\n"
        "\n")
    text2 = _("Вы действительно хотите изменить дату рождения <b>{name}</b> на <b>{new_day}.{new_month}</b>?\n"
              "\n")
    text3 = _("Год рождения не может быть больше текущего года.\n"
              "Введите корректный год рождения.\n"
              "Например: <b>1990</b>")

    text4 = _("Не правильный формат ввода.\n"
              "Введите год рождения в формате <b>гггг</b>.\n"
              "Например: <b>1990</b>")

    data = await state.get_data()
    name = data.get("name")
    new_day = data.get("new_day")
    new_month = data.get("new_month")

    if isinstance(target, Message):
        if not await correct_year_format(message=target.text):
            await target.answer(text=text4, reply_markup=add_year_keyboard())
        elif not await lower_than_current(message=target.text):
            await target.answer(text=text3, reply_markup=add_year_keyboard())
        else:
            new_year = target.text
            await target.answer(text=text.format(name=name, new_day=new_day, new_month=new_month, new_year=new_year),
                                reply_markup=approving_keyboard())
    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        new_year = None
        await target.message.answer(text2.format(name=name, new_day=new_day, new_month=new_month),
                                    reply_markup=approving_keyboard())
    else:
        return

    await state.update_data(new_year=new_year)
    await EditDateStates.waiting_for_date_edit_approve.set()


# Хэндлер для завершения редактирования даты с сохранением изменений в БД
async def date_editing_complete_handler(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    text = _("<b>Изменения успешно внесены</b>")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name")
    new_day = data.get("new_day")
    new_month = data.get("new_month")
    new_year = data.get("new_year")
    user_id = call.from_user.id
    await update_date_in_db(new_day=new_day, new_month=new_month, new_year=new_year, user_id=user_id, name=name)
    await call.message.answer(text=text, reply_markup=after_changes_keyboard())
    onday_id, before_id = await get_id_by_name(scheduler=scheduler, user_id=user_id, name=name)
    await modify_date(scheduler=scheduler, new_day=new_day, new_month=new_month, onday_id=onday_id, before_id=before_id)
    await state.finish()


def reg_edit_date_handlers(dp: Dispatcher):
    # Регистрация хендлеров многоуровнего меню "Изменить дату"
    dp.register_callback_query_handler(edit_date_handler, EditDateFilter(), state=EditPersonStates.waiting_for_what_to_edit)
    dp.register_message_handler(edit_year_handler, state=EditDateStates.waiting_for_day_month_instead)
    dp.register_callback_query_handler(check_before_save_date_handler, SkipFilter(), state=EditDateStates.waiting_for_year_instead)
    dp.register_message_handler(check_before_save_date_handler, state=EditDateStates.waiting_for_year_instead)
    dp.register_callback_query_handler(date_editing_complete_handler, ApproveDataFilter(),
                                       state=EditDateStates.waiting_for_date_edit_approve)


    # Регистрация хэндлеров кнопки "Назад" в ветке "Изменить дату"
    dp.register_callback_query_handler(edit_date_handler, BackMenuFilter(),
                                       state=EditDateStates.waiting_for_year_instead)
    dp.register_callback_query_handler(edit_year_handler, BackMenuFilter(),
                                       state=EditDateStates.waiting_for_date_edit_approve)