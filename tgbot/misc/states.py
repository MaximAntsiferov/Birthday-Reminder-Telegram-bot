from aiogram.dispatcher.filters.state import StatesGroup, State


class AddPersonStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_year = State()
    waiting_for_notification = State()
    waiting_for_saving = State()


class LookAtListStates(StatesGroup):
    waiting_for_action = State()


class DelPersonStates(StatesGroup):
    waiting_for_name_to_del = State()
    waiting_for_del_approve = State()


class EditPersonStates(StatesGroup):
    waiting_for_name_to_edit = State()
    waiting_for_what_to_edit = State()


class EditNameStates(StatesGroup):

    waiting_for_name_instead = State()
    waiting_for_name_edit_approve = State()


class EditDateStates(StatesGroup):

    waiting_for_day_month_instead = State()
    waiting_for_year_instead = State()
    waiting_for_date_edit_approve = State()


class EditNotificationStates(StatesGroup):

    waiting_for_notification_instead = State()
    waiting_for_notification_approve = State()
