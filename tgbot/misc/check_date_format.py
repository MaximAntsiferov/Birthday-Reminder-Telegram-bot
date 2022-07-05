import re
from datetime import date


# Проверка введенной даты на соответствие формату ДД.ММ
async def correct_date_format(message: str) -> bool:
    if re.fullmatch(r"(0[1-9]|1[0-9]|2[0-9]|3[01]).(0[1-9]|1[012])", message):
        return True
    return False


# Проверка введенного года на соответствие формату ГГГГ
async def correct_year_format(message: str) -> bool:
    if re.fullmatch(r"[0-9]{4}", message):
        return True
    return False


# Проверка введенного года: не должен превышать текущий год.
async def lower_than_current(message: str) -> bool:
    if int(message) <= date.today().year:
        return True
    return False
