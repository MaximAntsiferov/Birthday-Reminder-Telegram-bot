from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from middlewares.language_middleware import _


def main_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Добавить"), callback_data="add_note"),
            ],
            [
                InlineKeyboardButton(text=_("Смотреть список"), callback_data="watch_list")
            ],
            [
                InlineKeyboardButton(text=_("Выбрать язык"), callback_data="/language")
            ]
        ]
    )


def back_or_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("< Назад"), callback_data="back"),
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu")
            ],
        ]
    )


def add_year_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Пропустить"), callback_data="skip"),
            ],
            [
                InlineKeyboardButton(text=_("< Назад"), callback_data="back"),
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu")
            ],
        ]
    )


def add_notification_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("В день рождения"), callback_data="on_date"),
                InlineKeyboardButton(text=_("За три дня"), callback_data="three_days_before")
            ],
            [
                InlineKeyboardButton(text=_("Выбрать оба варинта"), callback_data="both_variants")
            ],
            [
                InlineKeyboardButton(text=_("< Назад"), callback_data="back"),
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu")
            ],
        ]
    )


def approving_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Все верно"), callback_data="accept"),
            ],
            [
                InlineKeyboardButton(text=_("< Назад"), callback_data="back"),
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu")
            ],
        ]
    )


def main_menu_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu"),
            ],
        ]
    )


def del_or_edit_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Удалить запись"), callback_data="del_note"),
                InlineKeyboardButton(text=_("Редактировать запись"), callback_data="edit_note")
            ],
            [
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu")
            ]
        ]
    )


def choose_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский", callback_data="ru"),
                InlineKeyboardButton(text="English", callback_data="en")
            ],
        ]
    )

def what_to_edit_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Имя"), callback_data="change_name"),
                InlineKeyboardButton(text=_("Дата"), callback_data="change_date"),
                InlineKeyboardButton(text=_("Уведомление"), callback_data="change_notification")
            ],
            [
                InlineKeyboardButton(text=_("< Назад"), callback_data="back"),
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu")
            ],
        ]
    )

def after_changes_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Смотреть список"), callback_data="watch_list"),
                InlineKeyboardButton(text=_("Главное меню"), callback_data="main menu")
            ],
        ]
    )