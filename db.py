import sqlite3
import dataclasses

sqlite_connection = sqlite3.connect('identifier.sqlite')
cursor = sqlite_connection.cursor()


@dataclasses.dataclass
class UserData:
    chat_id: int
    need_translation: bool
    requests_value: int
    context: str


def get_user_data(chat_id: int) -> (UserData | None):
    sqlite_select_query = f"""SELECT * from bot WHERE chat_id={chat_id}"""
    cursor.execute(sqlite_select_query)
    data = cursor.fetchone()
    if data is None:
        return None
    else:
        return UserData(
            chat_id=int(data[0]),
            need_translation=bool(int(data[1].replace('-', '0').replace('+', '1')))
        )


def init_user(chat_id: int):
    if get_user_data(chat_id) is None:
        cursor.execute(
            f"INSERT INTO bot (chat_id, need_translation, requests_value, context) VALUES ('{chat_id}', '-', 5, '');")
        sqlite_connection.commit()


def change_translation_status(chat_id: int, to_what_set: str):
    sql_update_query = f"""Update bot set need_translation = '{to_what_set}' where chat_id='{chat_id}';"""
    cursor.execute(sql_update_query)
    sqlite_connection.commit()


def clear_history(chat_id: int):
    sql_update_query = f"""Update bot set context='' where chat_id='{chat_id}';"""
    cursor.execute(sql_update_query)
    sqlite_connection.commit()


def update_requests_before_pay(chat_id: int, requests_value: int):
    sql_update_query = f"""Update bot set requests_value = {requests_value} where chat_id='{chat_id}';"""
    cursor.execute(sql_update_query)
    sqlite_connection.commit()


def update_request_context(chat_id: int, context: str):
    sql_update_query = f"""Update bot set context = '{context}' where chat_id='{chat_id}';"""
    cursor.execute(sql_update_query)
    sqlite_connection.commit()

