from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.item import ItemModel

ITEM_DELETED = "Item deleted"
ERROR_INSERTING = "An Error occurred inserting the item"
NAME_ALREADY_EXIST = "An item with name '{}' already exist"
ITEM_NOT_FOUND = "Item not found"
BLANK_ERROR = "'{}' cannot be left blank."


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": ITEM_NOT_FOUND}, 404

    # This ensures that a new item can be created wen u just logged in- fresh_toke_required
    # NOTE the parameter fresh, not refresh
    # Usage: to ensure a critical action requires user logging in or entering their password
    @jwt_required(fresh=True)
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXIST.format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)  # **data => data["price"], data["store_id"]
        try:
            item.save_to_db()
            print("ITEM DATA:=>  ", item.name, item.price, sep=", ")
        except:
            return {"message": ERROR_INSERTING}, 500  # Internal Server Error

        return item.json(), 201

    @classmethod    # this mus come first
    @jwt_required()
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}
        return {"message": ITEM_NOT_FOUND}

    @classmethod
    def put(cls, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data["price"]

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    # can be used to return some  data if user is logged in and another data if not logged in
    # optional=True means is not compulsory if user is logged in
    # @jwt_required(optional=True)
    # def get(self):
    #     user_id = get_jwt_identity()
    #     items = [item.json() for item in ItemModel.find_all()]
    #     if user_id:
    #         return {"items": items}, 200
    #     return {
    #         "items": [item["name"] for item in items],
    #         "message": "More data available if you login."
    #     }, 200
    @classmethod
    def get(cls):
        return {"items": [item.json() for item in ItemModel.find_all()]}, 200
