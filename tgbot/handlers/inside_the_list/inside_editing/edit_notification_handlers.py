from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.db import update_notifications_in_db
from tgbot.filters import BackMenuFilter, EditNoteFilter, ChooseNotificationFilter, ApproveDataFilter
from tgbot.keyboards import add_notification_keyboard, approving_keyboard, after_changes_keyboard
from tgbot.misc.notification_views import long_notification
from tgbot.misc.states import EditNotificationStates, EditPersonStates
from tgbot.middlewares.language_middleware import _
from tgbot.scheduler import get_id_by_name, modify_notification


# Хэндлер для меню "Изменить уведомление"
async def edit_notification_handler(call: CallbackQuery, state: FSMContext):
    text = _("Выберите когда напоминать Вам о Дне рождения <b>{name}</b>:")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name")
    await call.message.answer(text=text.format(name=name), reply_markup=add_notification_keyboard())
    await EditNotificationStates.waiting_for_notification_instead.set()


# Хэндлер для меню "Подтвердите введенные данные"
async def check_before_edit_notif_handler(call: CallbackQuery, state: FSMContext):
    text = _("Теперь бот будет напоминать Вам о день рождении <b>{name}</b>:\n\n"
             "<b>{notification}</b>\n"
             "\n"
             "Нажмите кнопку 'Все верно', чтобы сохранить данные изменения.")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name")
    long_note = await long_notification(call.data)
    await state.update_data(notification=call.data)
    await call.message.answer(text.format(name=name, notification=long_note), reply_markup=approving_keyboard())
    await EditNotificationStates.waiting_for_notification_approve.set()


# Хэндлер для завершения редактирования уведомлений с сохранением изменений в БД
async def notif_editing_complete_handler(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    text = _("<b>Изменения успешно внесены</b>")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name")
    year = data.get("year")
    month = data.get("month")
    day = data.get("day")
    notification = data.get("notification")
    user_id = call.from_user.id
    bot = Bot.get_current()
    await update_notifications_in_db(notification=notification, user_id=user_id, name=name)
    await call.message.answer(text=text, reply_markup=after_changes_keyboard())
    onday_id, before_id = await get_id_by_name(scheduler=scheduler, user_id=user_id, name=name)
    await modify_notification(scheduler=scheduler, bot=bot, notification=notification, user_id=user_id, name=name,
                              year=year, month=month, day=day, onday_id=onday_id, before_id=before_id)
    await state.finish()


def reg_edit_notification_handlers(dp: Dispatcher):
    # Регистрация хендлеров многоуровнего меню "Изменить уведомление"
    dp.register_callback_query_handler(edit_notification_handler, EditNoteFilter(),
                                       state=EditPersonStates.waiting_for_what_to_edit)
    dp.register_callback_query_handler(check_before_edit_notif_handler, ChooseNotificationFilter(),
                                       state=EditNotificationStates.waiting_for_notification_instead)
    dp.register_callback_query_handler(notif_editing_complete_handler, ApproveDataFilter(),
                                       state=EditNotificationStates.waiting_for_notification_approve)

    # Регистрация хэндлеров кнопки "Назад" в ветке "Изменить уведомление"
    dp.register_callback_query_handler(edit_notification_handler, BackMenuFilter(),
                                       state=EditNotificationStates.waiting_for_notification_approve)
