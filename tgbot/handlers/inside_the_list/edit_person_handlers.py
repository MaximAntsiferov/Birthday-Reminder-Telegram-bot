from typing import Union

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.db import get_person_from_db, exist_in_db
from tgbot.middlewares.language_middleware import _
from tgbot.misc.person_data_view import from_db_to_view
from tgbot.filters import BackMenuFilter, EditPersonFilter
from tgbot.keyboards import back_or_main_keyboard, what_to_edit_keyboard
from tgbot.misc.states import EditPersonStates, EditNameStates, EditDateStates, EditNotificationStates


# Хэндлер для меню "Изменить"
async def edit_person_handler(call: CallbackQuery):
    text = _("Введите имя человека, данные которого вы хотите отредактировать")

    await call.answer(cache_time=60)
    await call.message.answer(text=text, reply_markup=back_or_main_keyboard())
    await EditPersonStates.waiting_for_name_to_edit.set()


# Хэндлер для меню "Выберите данные для изменения"
async def what_to_edit_handler(target: Union[Message, CallbackQuery], state: FSMContext):
    text = _("Вы выбрали запись:\n"
             "\n")
    text2 = _("Такого имени нет в списке, проверьте правильность написания и введите имя еще раз:")
    text3 = _("Выберите какие данные Вы хотели бы изменить:")

    user_id = target.from_user.id
    if isinstance(target, Message):
        name = target.text
    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        data = await state.get_data()
        name = data.get("name")
        target = target.message
    else:
        return

    if await exist_in_db(name=name, user_id=user_id):
        data_from_db = await get_person_from_db(name=name, user_id=user_id)
        short_data = await from_db_to_view(data_from_db)
        text += (short_data + text3)
        await target.answer(text=text, reply_markup=what_to_edit_keyboard())

        await state.update_data(name=name, year=data_from_db['year'], month=data_from_db['month'],
                                day=data_from_db['day'])
        await EditPersonStates.waiting_for_what_to_edit.set()
    else:
        await target.answer(text=text2, reply_markup=back_or_main_keyboard())


def reg_edit_person_handlers(dp: Dispatcher):
    # Регистрация хэндлеров кнопки "Назад" в ветке "Смотреть список"
    dp.register_callback_query_handler(edit_person_handler, BackMenuFilter(),
                                       state=EditPersonStates.waiting_for_what_to_edit)
    dp.register_callback_query_handler(what_to_edit_handler, BackMenuFilter(),
                                       state=EditNameStates.waiting_for_name_instead)
    dp.register_callback_query_handler(what_to_edit_handler, BackMenuFilter(),
                                       state=EditDateStates.waiting_for_day_month_instead)
    dp.register_callback_query_handler(what_to_edit_handler, BackMenuFilter(),
                                       state=EditNotificationStates.waiting_for_notification_instead)

    # Регистрация хендлеров многоуровнего меню "Смотреть список"
    dp.register_callback_query_handler(edit_person_handler, EditPersonFilter(), state="*")
    dp.register_message_handler(what_to_edit_handler, state=EditPersonStates.waiting_for_name_to_edit)
