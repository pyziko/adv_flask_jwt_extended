from typing import Dict, Union

from db import db

# CUSTOM JSON TYPES
UserJSON = Dict[str, Union[int, str]]


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username: str, password: str):  # we are using _id because id is a python keyword
        self.username = username
        self.password = password

    def json(self) -> UserJSON:
        return {"id": self.id, "username": self.username}

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username) -> "UserModel":
        return cls.query.filter_by(username=username).first()  # .query ==> select * from users, .filter ==> where

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()
