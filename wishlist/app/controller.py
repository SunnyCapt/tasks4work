import pymysql

from random import randint
from settings import DBSettings


class _DBScheme:
    ID, TITLE, PRICE, LINK, NOTE = "id", "title", "price", "link", "note"
    columns = (ID, TITLE, PRICE, LINK, NOTE)
    title_max_char = 60
    link_max_char = 60
    note_max_char = 120

    sql_to_create_table = "CREATE TABLE IF NOT EXISTS wish(" \
                          "id INT PRIMARY KEY AUTO_INCREMENT," \
                          f"title VARCHAR({title_max_char}) NOT NULL," \
                          "price DOUBLE NOT NULL," \
                          f"link VARCHAR({link_max_char}) NOT NULL," \
                          f"note VARCHAR({note_max_char}));"

    sql_to_insert_row = f"INSERT INTO `wish` (" + \
                        ', '.join(f"`{c}`" for c in columns[1:]) + \
                        f") VALUES (" + \
                        ', '.join(['%s'] * len(columns[1:])) + \
                        f")"

    sql_to_select_rows = "SELECT " + \
                         ', '.join(f"`{c}`" for c in columns) + \
                         " FROM `wish` ORDER BY id LIMIT %s OFFSET %s"

    sql_to_get_count = "SELECT count(*) FROM `wish`"
    
    sql_to_delete_row = f"DELETE FROM `wish` WHERE id=%s"

    @classmethod
    def get_sql_to_update_row(cls, arg_to_update):
        if arg_to_update not in cls.columns:
            raise Exception(f"WTF: {arg_to_update}")
        return f"UPDATE `wish` SET {arg_to_update}=%s WHERE id=%s"

    
class Controller:
    def __init__(self, settings=DBSettings):
        self._connection = pymysql.connect(
            host=settings.host,
            port=settings.port,
            user=settings.user,
            password=settings.password,
            db=settings.name,
            charset=settings.charset
        )
        self._execute(_DBScheme.sql_to_create_table)

    def _execute(self, sql, *args):
        with self._connection:
            cursor = self._connection.cursor()
            cursor.execute(sql, args)
            return cursor.fetchall()

    def create(self, title, price, link, note='') -> None:
        """
        Convertes, validates and creates a new wish.

        :param title: title of the wish
        :param price: price of the wish, can be numeric string
        :param link: link to the wish
        :param note: some your note about th wish (default None)
        :exception ValueError: when args is wrong
        """
        wish = {
            "title": title,
            "price": price,
            "link": link,
            "note": note
        }

        wish = self._converte(**wish)
        self._validate(**wish)

        self._execute(_DBScheme.sql_to_insert_row, *(wish[key] for key in _DBScheme.columns[1:]))

    def read(self, count=5, offset=0) -> tuple:
        """
        :return: list with wish-tupels
        """

        return self._execute(
            _DBScheme.sql_to_select_rows,
            count,
            offset
        )

    def update(self, to_update: dict) -> None:
        """
        Convertes, validates and updates a wish.

        :param to_update: dictionary with id and value of another column to update
        :exception ValueError: when args is wrong
        """
        to_update = self._converte(**to_update)
        self._validate(**to_update)
        if len(to_update.items()) != 2:
            raise Exception("WTF: wrong data to update")

        wish_id = to_update["id"]
        to_update.pop("id")

        self._execute(
            _DBScheme.get_sql_to_update_row(list(to_update.keys())[0]),
            list(to_update.values())[0],
            wish_id
        )

    def delete(self, row_id: int) -> None:
        """
        Deletes by id.

        :param row_id:
        """
        id_dict = {"id": row_id}
        id_dict = self._converte(**id_dict)

        self._execute(
            _DBScheme.sql_to_delete_row,
            id_dict["id"]
        )

    def count(self):
        """
        :return: count of wishes.
        """
        return self._execute(_DBScheme.sql_to_get_count)[0][0]

    def _converte(self, **kwargs):
        for key, value in kwargs.items():
            if key == _DBScheme.PRICE:
                kwargs[key] = float(value)
            elif key == _DBScheme.ID:
                kwargs[key] = int(value)
        return kwargs

    def _validate(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key == _DBScheme.TITLE:
                if len(value) > _DBScheme.title_max_char:
                    raise ValueError("Very long title")
                if not value:
                    raise ValueError("Title can not be empty")
            elif key == _DBScheme.PRICE and value < 0:
                raise ValueError("Price cant not be negative")
            elif key == _DBScheme.LINK:
                if len(value) > _DBScheme.link_max_char:
                    raise ValueError("Very long link")
                if not value:
                    raise ValueError("Link can not be empty")
            elif key == _DBScheme.NOTE and len(value) > _DBScheme.note_max_char:
                raise ValueError("Very long note")

