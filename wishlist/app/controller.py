from random import randint
from settings import ControllerSettings


class Controller:
    _db = [
        {
            "id": i,
            "title": "external hard drive",
            "price": 3070.75,
            "link": "https://www.citilink.ru/catalog/computers_and_notebooks/media/hdd_out/294583/",
            "note": "".join(chr(randint(97, 122)) for _ in range(15))
        }
        for i in range(1, 15)
    ]  # id[int][notnull], title[str][notnull], price[float][notnull], link[str][notnull], note[str][nullable]

    ID, TITLE, PRICE, LINK, NOTE = "id", "title", "price", "link", "note"
    _keys = (ID, TITLE, PRICE, LINK, NOTE)

    def __init__(self, settings=ControllerSettings):
        self.settings = settings

    def _to_tuple(self, wish):
        return tuple(wish[key] for key in self._keys)

    def create(self, title, price, link, note=None) -> tuple:
        """
        Convertes, validates and creates a new wish.

        :param title: title of the wish
        :param price: price of the wish, can be numeric string
        :param link: link to the wish
        :param note: some your note about th wish (default None)
        :return: created wish row (with id)
        :exception ValueError: when args is wrong
        """
        wish_id = self._db[-1]["id"] + 1 if self._db else 1
        wish = {
            "id": wish_id,
            "title": title,
            "price": price,
            "link": link,
            "note": note
        }

        wish = self._converte(**wish)
        self._validate(**wish)

        self._db.append(wish)
        return self._to_tuple(wish)

    def read(self, count=5, offset=0) -> list:
        """
        Returns list with wish-tupels
        """
        if offset + 1 > len(self._db):
            return []

        start_index, end_index = offset, offset + count
        end_index = len(self._db) if end_index > len(self._db) else end_index

        return [self._to_tuple(wish) for wish in self._db[offset:end_index]]

    def update(self, to_update: dict) -> tuple:
        """
        Convertes, validates and updates a wish.
        Returns tuple with created wish row.

        :param to_update: dict with data to update
        :exception ValueError: when args is wrong
        """
        to_update = self._converte(**to_update)
        self._validate(**to_update)

        row_index = self._index(to_update["id"])
        if row_index == -1:
            raise Exception("Not found")

        for key, value in to_update.items():
            self._db[row_index][key] = value
        return self._to_tuple(self._db[row_index])

    def delete(self, row_id: int) -> tuple:
        """
        Deletes and returns wish by id.

        :param row_id:
        """
        row_index = self._index(row_id)
        if row_index == -1:
            raise Exception("Not found")
        return self._to_tuple(self._db.pop(row_index))

    def count(self):
        return len(self._db)

    def _converte(self, **kwargs):
        for key, value in kwargs.items():
            if key == self.PRICE:
                kwargs[key] = float(value)
            elif key == self.ID:
                kwargs[key] = int(value)
        return kwargs

    def _validate(self, **kwargs) -> None:
        if self.ID not in kwargs and set(kwargs.keys()) ^ (set(self._keys) - {ID}):
            raise ValueError("Not enought args")
        for key, value in kwargs.items():
            if key == self.TITLE:
                if len(value) > self.settings.db_scheme.title_max_char:
                    raise ValueError("Very long title")
                if not value:
                    raise ValueError("Title can not be empty")
            elif key == self.PRICE and value < 0:
                raise ValueError("Price cant not be negative")
            elif key == self.LINK:
                if len(value) > self.settings.db_scheme.link_max_char:
                    raise ValueError("Very long link")
                if not value:
                    raise ValueError("Link can not be empty")
            elif key == self.NOTE and len(value) > self.settings.db_scheme.note_max_char:
                raise ValueError("Very long note")

    def _index(self, row_id):
        for i, row in enumerate(self._db):
            if row["id"] == row_id:
                return i
        return -1
