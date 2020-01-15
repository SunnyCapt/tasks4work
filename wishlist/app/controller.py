class Controller:
    _db = [
        {
            "id": i,
            "title": "external hard drive",
            "price": 3070.75,
            "link": "https://www.citilink.ru/catalog/computers_and_notebooks/media/hdd_out/294583/",
            "note": "some note"
        }
        for i in range(1, 12)
    ]  # id[int][notnull], title[str][notnull], price[float][notnull], link[str][notnull], note[str][nullable]

    _keys = ("id", "title", "price", "link", "note")

    def __init__(self, settings=None):
        pass

    def _to_tuple(self, wish):
        return tuple(wish[key] for key in self._keys)

    def create(self, title: str, price: float, link: str, note=None) -> tuple:
        wish_id = self._db[-1]["id"] + 1 if self._db else 1
        wish = {
            "id": wish_id,
            "title": title,
            "price": price,
            "link": link,
            "note": note
        }
        self._db.append(wish)
        return self._to_tuple(wish)

    def read(self, count=5, offset=0) -> list:
        if offset + 1 > len(self._db):
            return []

        start_index, end_index = offset, offset + count
        end_index = len(self._db) if end_index > len(self._db) else end_index

        return [self._to_tuple(wish) for wish in self._db[offset:end_index]]

    def update(self, updated: dict) -> tuple:
        if not self._is_valid(updated):
            raise Exception("wrong field names")

        row_index = self._index(updated["id"])
        if row_index == -1:
            raise Exception("Not found")

        for key, value in updated.items():
            self._db[row_index][key] = value
        return self._to_tuple(self._db[row_index])

    def delete(self, row_id) -> tuple:
        row_index = self._index(row_id)
        if row_index == -1:
            raise Exception("Not found")
        return self._to_tuple(self._db.pop(row_index))

    def count(self):
        return len(self._db)

    def _index(self, row_id):
        for i, row in enumerate(self._db):
            if row["id"] == row_id:
                return i
        return -1

    def _is_valid(self, updated):
        return not (bool(set(updated) - set(self._keys)) and "id" in updated)
