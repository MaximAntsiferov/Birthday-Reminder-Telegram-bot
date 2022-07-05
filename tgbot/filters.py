from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery


# Срабатывает при нажатии кнопки "Главное меню"
class MainMenuFilter(BoundFilter):

    async def check(self, call: CallbackQuery, state: FSMContext = None):
        if call.data == "main menu":
            return True
        return False


# Срабатывает при нажатии кнопки "Выбрать язык"
class ChooseLanguageFilter(BoundFilter):

    async def check(self, call: CallbackQuery, state: FSMContext = None):
        if call.data == "/language":
            return True
        return False


# Срабатывает при нажатии кнопок "Русский" или "English"
class SetLanguageFilter(BoundFilter):

    async def check(self, call: CallbackQuery, state: FSMContext = None):
        if call.data == "ru" or call.data == "en":
            return True
        return False


# Срабатывает при нажатии кнопки "< Назад"
class BackMenuFilter(BoundFilter):

    async def check(self, call: CallbackQuery, state: FSMContext = None):
        if call.data == "back":
            return True
        return False


# Срабатывает при нажатии кнопки "Добавить"
class AddNoteFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "add_note":
            return True
        return False


# Срабатывает при нажатии кнопки "Все верно"
class ApproveDataFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "accept":
            return True
        return False


# Срабатывает при нажатии кнопок "В день рождения", "За три дня" или "Оба варианта"
class ChooseNotificationFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "on_date" or call.data == "three_days_before" or call.data == "both_variants":
            return True
        return False


# Срабатывает при нажатии кнопки "Смотреть список"
class LookAtListFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "watch_list":
            return True
        return False


# Срабатывает при нажатии кнопки "Удалить"
class DelPersonFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "del_note":
            return True
        return False


# Срабатывает при нажатии кнопки "Изменить"
class EditPersonFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "edit_note":
            return True
        return False


# Срабатывает при нажатии кнопки "Имя"
class EditNameFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "change_name":
            return True
        return False


# Срабатывает при нажатии кнопки "Дата"
class EditDateFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "change_date":
            return True
        return False


# Срабатывает при нажатии кнопки "Уведомление"
class EditNoteFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "change_notification":
            return True
        return False


# Срабатывает при нажатии кнопки "Пропустить"
class SkipFilter(BoundFilter):

    async def check(self, call: CallbackQuery):
        if call.data == "skip":
            return True
        return False


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(MainMenuFilter)
    dp.filters_factory.bind(BackMenuFilter)
    dp.filters_factory.bind(AddNoteFilter)
    dp.filters_factory.bind(ChooseNotificationFilter)
    dp.filters_factory.bind(ApproveDataFilter)
    dp.filters_factory.bind(LookAtListFilter)
    dp.filters_factory.bind(DelPersonFilter)
    dp.filters_factory.bind(ChooseLanguageFilter)
    dp.filters_factory.bind(SetLanguageFilter)
    dp.filters_factory.bind(EditPersonFilter)
    dp.filters_factory.bind(EditNameFilter)
    dp.filters_factory.bind(EditDateFilter)
    dp.filters_factory.bind(EditNoteFilter)
    dp.filters_factory.bind(SkipFilter)

