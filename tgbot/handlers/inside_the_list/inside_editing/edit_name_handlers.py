from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.db import exist_in_db, update_name_in_db
from tgbot.filters import BackMenuFilter, EditNameFilter, ApproveDataFilter
from tgbot.keyboards import back_or_main_keyboard, after_changes_keyboard, approving_keyboard
from tgbot.misc.states import EditPersonStates, EditNameStates
from tgbot.middlewares.language_middleware import _
from tgbot.scheduler import get_id_by_name, modify_name


# Хэндлер для меню "Изменить имя"
async def edit_name_handler(call: CallbackQuery):
    text = _("Введите новое имя")

    await call.answer(cache_time=60)
    await call.message.answer(text=text, reply_markup=back_or_main_keyboard())
    await EditNameStates.waiting_for_name_instead.set()


# Хэндлер для меню "Подтвердить новое имя"
async def check_before_edit_name_handler(message: Message, state: FSMContext):
    text = _("Вы действительно хотите изменить имя <b>{name}</b> на имя <b>{new_name}</b>?\n"
             "\n")
    text2 = _("Такое имя уже есть в Вашем списке. Введите уникальное имя.")

    new_name = message.text
    if await exist_in_db(name=new_name, user_id=message.from_user.id):
        await message.answer(text2, reply_markup=back_or_main_keyboard())
    else:
        data = await state.get_data()
        name = data.get("name")
        await message.answer(text.format(name=name, new_name=new_name), reply_markup=approving_keyboard())
        await state.update_data(new_name=new_name)
        await EditNameStates.waiting_for_name_edit_approve.set()


# Хэндлер для завершения редактирования имени с сохранением изменений в БД
async def name_editing_complete_handler(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    text = _("<b>Изменения успешно внесены</b>")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name")
    new_name = data.get("new_name")
    user_id = call.from_user.id
    await update_name_in_db(old_name=name, new_name=new_name, user_id=user_id)
    await call.message.answer(text=text, reply_markup=after_changes_keyboard())
    onday_id, before_id = await get_id_by_name(scheduler=scheduler, user_id=user_id, name=name)
    await modify_name(scheduler=scheduler, user_id=user_id, new_name=new_name, onday_id=onday_id, before_id=before_id)
    await state.finish()


def reg_edit_name_handlers(dp: Dispatcher):
    # Регистрация хендлеров многоуровнего меню "Изменить имя"
    dp.register_callback_query_handler(edit_name_handler, EditNameFilter(),
                                       state=EditPersonStates.waiting_for_what_to_edit)
    dp.register_message_handler(check_before_edit_name_handler, state=EditNameStates.waiting_for_name_instead)
    dp.register_callback_query_handler(name_editing_complete_handler, ApproveDataFilter(),
                                       state=EditNameStates.waiting_for_name_edit_approve)

    # Регистрация хэндлеров кнопки "Назад" в ветке "Изменить имя"
    dp.register_callback_query_handler(edit_name_handler, BackMenuFilter(),
                                       state=EditNameStates.waiting_for_name_edit_approve)
