from middlewares.language_middleware import i18n


# Функция для извлечения текста и перевода на английский язык, если такой выбран пользователем
_ = i18n.gettext


# Функция определяет как будут выглядеть короткие и длинные варианты типов напоминаний
async def short_notification(notification: str):
    if notification == "on_date":
        return _("В день")
    elif notification == "three_days_before":
        return _("За три дня")
    elif notification == "both_variants":
        return _("Оба варианта")
    else:
        return


async def long_notification(notification: str):
    if notification == "on_date":
        return _("- в День рождения в 9:00")
    elif notification == "three_days_before":
        return _("- за 3 дня до Дня рождения")
    elif notification == "both_variants":
        return _("- в День рождения в 9:00\n- за 3 дня до Дня рождения")
    else:
        return

