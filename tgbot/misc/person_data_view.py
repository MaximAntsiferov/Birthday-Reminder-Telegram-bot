import asyncpg

from tgbot.misc.notification_views import short_notification


# Функция определяет как будет выглядеть информация о человеке в списке Дней рождений
async def from_db_to_view(data: asyncpg.Record) -> str:
    short_note = await short_notification(data['notification'])
    if data['year'] is not None:
        return f"<b>{data['name']} | {data['day']:02}.{data['month']:02}.{data['year']} | {short_note}\n\n</b>"
    else:
        return f"<b>{data['name']} | {data['day']:02}.{data['month']:02} | {short_note}\n\n</b>"