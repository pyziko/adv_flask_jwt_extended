from typing import List, Union, Dict

from db import db
from models.item import ItemJSON

# CUSTOM JSON TYPES
# returning descriptive Json
StoreJSON = Dict[str, Union[int, str, List[ItemJSON]]]


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    items = db.relationship(
        "ItemModel", lazy="dynamic"
    )  # this is lazy loading for one => many relationship

    def __init__(self, name: str):
        self.name = name

    # todo INFO: we added .all() to support lazy loading
    # based in lazy loading above, until we call store.json(), items are not fetched
    def json(self) -> StoreJSON:
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.json() for item in self.items.all()],
        }

    @classmethod
    def find_by_name(cls, name) -> "StoreModel":
        return cls.query.filter_by(name=name).first()  # SELECT * FROM items WHERE name=name LIMIT 1

    @classmethod
    def find_all(cls) -> List["StoreModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
