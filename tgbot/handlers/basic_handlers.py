from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from tgbot.filters import MainMenuFilter, ChooseLanguageFilter, SetLanguageFilter
from tgbot.keyboards import main_menu_keyboard, choose_language_keyboard, main_menu_button
from tgbot.middlewares.language_middleware import i18n, _
from tgbot.db import set_lang_to_db


# Хэндлер для команды "/start" и кнопки "Главное меню"
async def start_handler(target: Message | CallbackQuery, state: FSMContext):
    text = _("Добро пожаловать в <b>Birthday Reminder!</b>\n"
             "\n"
             "Добавьте человека, указав его имя и дату рождения.\n"
             "Бот напомнит Вам когда наступит его День Рождения.\n")

    await state.finish()
    if isinstance(target, Message):
        await target.answer(text=text, reply_markup=main_menu_keyboard())
    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        await target.message.answer(text=text, reply_markup=main_menu_keyboard())
    else:
        return


# Хэндлер для команды "/language" и кнопки "Выбрать язык"
async def choose_language_handler(target: Message | CallbackQuery, state: FSMContext):
    text = _("Выберите удобный для Вас язык")

    await state.finish()
    if isinstance(target, Message):
        await target.answer(text=text, reply_markup=choose_language_keyboard())
    elif isinstance(target, CallbackQuery):
        await target.answer(cache_time=60)
        await target.message.answer(text=text, reply_markup=choose_language_keyboard())
    else:
        return


# Хэндлер установки выбранного языка с записью в БД
async def set_language_handler(call: CallbackQuery):
    await call.answer(cache_time=60)
    i18n.ctx_locale.set(call.data)
    text = _("Русский язык установлен")
    await set_lang_to_db(user_id=call.from_user.id, lang=call.data)
    await call.message.answer(text=text, reply_markup=main_menu_button())


# Регистрация хендлеров
def reg_basic_handlers(dp: Dispatcher):

    # Регистрация хэндлеров команды /start и кнопки "Главное меню"
    dp.register_message_handler(start_handler, CommandStart(), state="*")
    dp.register_callback_query_handler(start_handler, MainMenuFilter(), state="*")

    # Регистрация хэндлеров команды /language и кнопки "Выбрать язык"
    dp.register_message_handler(choose_language_handler, commands="language", state="*")
    dp.register_callback_query_handler(choose_language_handler, ChooseLanguageFilter(), state="*")
    dp.register_callback_query_handler(set_language_handler, SetLanguageFilter(), state="*")