import asyncpg
import logging

from tgbot.config import DB_HOST, DB_USER, DB_PASS, DB_NAME


# Cоединение с БД
async def connection_to_db() -> asyncpg.Connection:
    connection: asyncpg.Connection = await asyncpg.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    logging.info("Соединение с БД установлено")
    return connection


# Закрытие соединения с БД
async def close_connection(connection: asyncpg.Connection):
    await connection.close()
    logging.info("Соединение с БД закрыто")


# Создание таблиц, содержащих список Дней Рождений и список языков
async def create_tables():
    connection = await connection_to_db()
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS birthdays(
        id serial PRIMARY KEY,
        user_id integer,
        name text,
        day integer,
        month integer,
        year integer,
        notification text
        )""")

    await connection.execute("""
        CREATE TABLE IF NOT EXISTS languages(
        id serial PRIMARY KEY,
        user_id integer,
        lang text
        )""")

    logging.info("Таблицы созданы или уже существуют")
    await close_connection(connection)


# Запрос языка из БД
async def get_lang_from_db(user_id: int) -> str | None:
    connection = await connection_to_db()
    value = await connection.fetch(f"SELECT lang FROM languages WHERE user_id='{user_id}'")
    await close_connection(connection)
    if len(value) > 0:
        return value[0]["lang"]
    else:
        return None


# Запись языка в БД
async def set_lang_to_db(user_id: int, lang: str) -> str:
    connection = await connection_to_db()
    value = await connection.fetch(f"SELECT user_id FROM languages WHERE user_id = '{user_id}'")
    if len(value) == 0:
        await connection.execute(f"INSERT INTO languages(user_id, lang) VALUES($1, $2)", user_id, lang)
    else:
        await connection.execute(f"UPDATE languages SET lang = '{lang}' WHERE user_id = '{user_id}'")
    await close_connection(connection)
    return lang


# Добавление записи в БД
async def add_person_to_db(user_id: int, name: str, day: str, month: str, year: str | None, notification: str):
    connection = await connection_to_db()
    await connection.execute("INSERT INTO birthdays(user_id, name, day, month, year, notification) "
                             "VALUES($1, $2, $3, $4, $5, $6)",
                             user_id, name, int(day), int(month), int(year) if year is not None else year, notification)
    await close_connection(connection)




# Запрос списка дней рождений из БД
async def get_data_from_db(user_id: int) -> list[asyncpg.Record]:
    connection = await connection_to_db()
    values = await connection.fetch(f"SELECT * FROM birthdays WHERE user_id ='{user_id}' ORDER BY month, day")
    await close_connection(connection)
    return values


# Проверка на наличие имени в БД
async def exist_in_db(name: str, user_id: int) -> bool:
    connection = await connection_to_db()
    value = await connection.fetch(f"SELECT name FROM birthdays WHERE user_id ='{user_id}' AND name = '{name}'")
    await close_connection(connection)
    if len(value) > 0:
        return True
    else:
        return False


# Запрос данных имени из БД
async def get_person_from_db(name: str, user_id: int) -> str:
    connection = await connection_to_db()
    values = await connection.fetch(f"SELECT * FROM birthdays WHERE user_id ='{user_id}' AND name = '{name}'")
    await close_connection(connection)
    data = values[0]
    return data


# Удаление имени из БД
async def del_from_db(name: str, user_id: int):
    connection = await connection_to_db()
    await connection.execute(f"DELETE FROM birthdays WHERE name = '{name}' AND user_id = '{user_id}'")
    await close_connection(connection)


# Обновление имени в БД
async def update_name_in_db(old_name: str, new_name: str, user_id: int):
    connection = await connection_to_db()
    await connection.execute(
        f"UPDATE birthdays SET name = '{new_name}' WHERE user_id = '{user_id}' AND name = '{old_name}'")
    await close_connection(connection)


# Обновление даты в БД
async def update_date_in_db(new_day: str, new_month: str, new_year: str, user_id: int, name: str):
    connection = await connection_to_db()
    await connection.execute(f"UPDATE birthdays SET day = $1, month = $2, year = $3 WHERE user_id = $4 AND name = $5",
                             int(new_day), int(new_month), int(new_year) if new_year is not None else new_year, user_id,
                             name)
    await close_connection(connection)


# Обновление уведомлений в БД
async def update_notifications_in_db(notification: str, user_id: int, name: str):
    connection = await connection_to_db()
    await connection.execute(
        f"UPDATE birthdays SET notification = '{notification}' WHERE user_id = '{user_id}' AND name = '{name}'")
    await close_connection(connection)
