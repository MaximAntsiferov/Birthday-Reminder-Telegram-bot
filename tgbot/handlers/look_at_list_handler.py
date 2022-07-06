from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from tgbot.db import get_data_from_db
from tgbot.filters import BackMenuFilter, LookAtListFilter
from tgbot.keyboards import del_or_edit_keyboard
from tgbot.middlewares.language_middleware import _
from tgbot.misc.notification_views import short_notification

from tgbot.misc.states import DelPersonStates, EditPersonStates, LookAtListStates


# Хэндлер для меню "Смотреть список"
async def look_at_list_handler(call: CallbackQuery):
    text = _("<b>Ваш список дней рождений:</b>\n")
    text2 = [_("\n<b>Январь</b>\n"), _("\n<b>Февраль</b>\n"), _("\n<b>Март</b>\n"), _("\n<b>Апрель</b>\n"),
             _("\n<b>Май</b>\n"), _("\n<b>Июнь</b>\n"), _("\n<b>Июль</b>\n"), _("\n<b>Август</b>\n"),
             _("\n<b>Сентябрь</b>\n"), _("\n<b>Октябрь</b>\n"), _("\n<b>Ноябрь</b>\n"), _("\n<b>Декабрь</b>\n")]
    text3 = _("\n"
              "<i>*Кликните по имени, чтобы скопировать</i>")

    await call.answer(cache_time=60)
    user_id = call.from_user.id
    records = await get_data_from_db(user_id)

    months_counter = 1
    answer = text
    for month_header in text2:
        for data in records:
            if data["month"] == months_counter:
                answer += month_header
                break

        for data in records:
            short_note = await short_notification(data['notification'])
            if data["month"] == months_counter and data["year"] is not None:
                answer += f"<code>{data['name']}</code> | {data['day']:02}.{data['month']:02}.{data['year']} | {short_note}\n"
            elif data["month"] == months_counter and data["year"] is None:
                answer += f"<code>{data['name']}</code> | {data['day']:02}.{data['month']:02} | {short_note}\n"
            else:
                continue
        months_counter += 1
    answer += text3

    await call.message.answer(text=answer, reply_markup=del_or_edit_keyboard())
    await LookAtListStates.waiting_for_action.set()


def reg_look_at_list_handler(dp: Dispatcher):
    # Регистрация хендлера многоуровнего меню "Смотреть список"
    dp.register_callback_query_handler(look_at_list_handler, LookAtListFilter(), state="*")

    # Регистрация хэндлеров кнопки "Назад" в ветке "Смотреть список"
    dp.register_callback_query_handler(look_at_list_handler, BackMenuFilter(), state=DelPersonStates.waiting_for_name_to_del)
    dp.register_callback_query_handler(look_at_list_handler, BackMenuFilter(), state=EditPersonStates.waiting_for_name_to_edit)


