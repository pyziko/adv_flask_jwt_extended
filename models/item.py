import datetime
from typing import Dict, List, Union

from db import db

# CUSTOM JSON TYPES
# giving detailed description as to what our JSON will return
# JSON below has key str, but value ::: str, float and int, hence we can consolidate with Union
ItemJSON = Dict[str, Union[int, str, float]]


class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    price = db.Column(db.Float(precision=2))
    request_id = db.Column(db.String(15))

    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    store = db.relationship('StoreModel')

    def __init__(self, name: str, price: float, store_id: int):
        self.name = name
        self.price = price
        self.store_id = store_id

    def json(self) -> ItemJSON:
        return {"id": self.id, "name": self.name, "price": self.price, "store_id": self.store_id,
                "request_id": self.request_id}

    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        return cls.query.filter_by(name=name).first()  # SELECT * FROM items WHERE name=name LIMIT 1

    @classmethod
    def find_all(cls) -> List:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        print("BEFORE COMMIT: ->", self.id)
        db.session.commit()
        print("AFTER COMMIT: ->", self.id)
        self.request_id = str(datetime.date.today().strftime("%b%y%d")).upper() + "-" + str(self.id)
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
