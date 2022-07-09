from tgbot.middlewares.language_middleware import _


# Функция определяет как будет выглядеть длинный вариант типов напоминаний
async def short_notification(notification: str) -> str:
    if notification == "on_date":
        return _("В день")
    elif notification == "three_days_before":
        return _("За три дня")
    elif notification == "both_variants":
        return _("Оба варианта")
    else:
        return


# Функция определяет как будет выглядеть короткий вариант типов напоминаний
async def long_notification(notification: str) -> str:
    if notification == "on_date":
        return _("- в День рождения")
    elif notification == "three_days_before":
        return _("- за 3 дня до Дня рождения")
    elif notification == "both_variants":
        return _("- в День рождения\n- за 3 дня до Дня рождения")
    else:
        return
