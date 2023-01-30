from mysql.connector import connect, Error
from config_data import config
from datetime import datetime


def database_creation() -> None:
    try:
        with connect(
                host=config.db_host,
                user=config.db_user,
                password=config.db_password
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE search_history")

    except Exception as ex:
        print(ex)


def table_creation() -> None:
    try:
        with connect(
                host=config.db_host,
                user=config.db_user,
                password=config.db_password,
                database="search_history"
        ) as connection:
            cursor = connection.cursor()
            create_table_query = ("CREATE TABLE user_history"
                                  "(id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,"
                                  "user_id INT NOT NULL,"
                                  "command VARCHAR(255) NOT NULL,"
                                  "`date` DATETIME NOT NULL,"
                                  "results TINYTEXT NOT NULL);"
                                  )
            cursor.execute(create_table_query)
            connection.commit()

    except Exception as ex:
        print(ex)


def table_insert(user_id: int, command: str, date: datetime, results: str) -> None:
    try:
        with connect(
            host=config.db_host,
            user=config.db_user,
            password=config.db_password,
            database="search_history"
        ) as connection:
            cursor = connection.cursor()
            insert_query = (f"INSERT INTO user_history(user_id, command, date, results) VALUES ({user_id}, "
                            f"'{command}', "
                            f"'{date}', "
                            f"'{results}');")
            cursor.execute(insert_query)
            connection.commit()
    except Exception as ex:
        print(ex)


def database_query(user_id: int, command: str, date: datetime, results: str) -> None:
    try:
        with connect(
            host=config.db_host,
            user=config.db_user,
            password=config.db_password
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'search_history';")
            if cursor.fetchall():
                table_insert(user_id=user_id, command=command, date=date, results=results)
            else:
                database_creation()
                table_creation()
                table_insert(user_id=user_id, command=command, date=date, results=results)

    except Exception as ex:
        print(ex)


def table_query(user_id: int) -> list:
    try:
        with connect(
                host=config.db_host,
                user=config.db_user,
                password=config.db_password,
                database="search_history"
        ) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT command, date, results FROM user_history WHERE user_id = {user_id}")
            return cursor.fetchall()
    except Exception as ex:
        print(ex)
