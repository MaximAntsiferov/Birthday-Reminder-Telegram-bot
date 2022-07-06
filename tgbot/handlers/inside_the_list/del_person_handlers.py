from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.db import exist_in_db, get_person_from_db, del_from_db
from tgbot.filters import DelPersonFilter, ApproveDataFilter, BackMenuFilter
from tgbot.middlewares.language_middleware import _

from tgbot.keyboards import back_or_main_keyboard, approving_keyboard, main_menu_button
from tgbot.misc.person_data_view import from_db_to_view
from tgbot.misc.states import DelPersonStates
from tgbot.scheduler import del_from_scheduler, get_id_by_name


# Хэндлер для меню "Удалить"
async def del_person_handler(call: CallbackQuery):
    text = _("Введите имя человека, которого хотите удалить из списка")

    await call.answer(cache_time=60)
    await call.message.answer(text=text, reply_markup=back_or_main_keyboard())
    await DelPersonStates.waiting_for_name_to_del.set()


# Хэндлер для меню "Подтвердите удаление"
async def check_before_del_handler(message: Message, state: FSMContext):
    text = _("Вы действительно хотите удалить запись со следующими данными:\n"
             "\n")
    text2 = _("Такого имени нет в списке, проверьте правильность написания и введите имя еще раз:")

    name = message.text
    user_id = message.from_user.id

    if await exist_in_db(name=name, user_id=user_id):
        data_from_db = await get_person_from_db(name=name, user_id=user_id)
        short_data = await from_db_to_view(data_from_db)
        text += short_data
        await message.answer(text=text, reply_markup=approving_keyboard())
        await state.update_data(name_to_del=message.text)
        await DelPersonStates.waiting_for_del_approve.set()
    else:
        await message.answer(text2, reply_markup=back_or_main_keyboard())


# Хэндлер для удаления из БД
async def deleting_complete_handler(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    text = _("Напоминание о День рождении <b>{name}</b> удалено.")

    await call.answer(cache_time=60)
    data = await state.get_data()
    name = data.get("name_to_del")
    user_id = call.from_user.id
    await del_from_db(name=name, user_id=user_id)
    await call.message.answer(text=text.format(name=name), reply_markup=main_menu_button())
    await state.finish()
    onday_id, before_id = await get_id_by_name(scheduler=scheduler, user_id=user_id, name=name)
    await del_from_scheduler(scheduler=scheduler, onday_id=onday_id, before_id=before_id)


def reg_del_person_handlers(dp: Dispatcher):
    # Регистрация хендлера многоуровнего меню "Удалить"
    dp.register_callback_query_handler(del_person_handler, DelPersonFilter(), state="*")
    dp.register_message_handler(check_before_del_handler, state=DelPersonStates.waiting_for_name_to_del)
    dp.register_callback_query_handler(deleting_complete_handler, ApproveDataFilter(),
                                       state=DelPersonStates.waiting_for_del_approve)

    # Регистрация хэндлеров кнопки "Назад" в ветке "Удалить"
    dp.register_callback_query_handler(del_person_handler, BackMenuFilter(),
                                       state=DelPersonStates.waiting_for_del_approve)
