import hmac

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
)
from flask_restful import Resource, reqparse

from blacklist import BLACKLIST_LOGOUT
from models.user import UserModel

BLANK_ERROR = "'{}' cannot be left blank"

SUCCESSFULLY_LOGGED_OUT = "Successfully logged out"
INVALID_CREDENTIALS = "Invalid credentials"
USER_DELETED = "User deleted"
USER_NOT_FOUND = "user not found"
USER_CREATED_SUCCESSFULLY = "User created successfully"
USERNAME_ALREADY_EXISTS = "User with username '{}' already exists"

_user_parser = reqparse.RequestParser()
_user_parser.add_argument("username", type=str, required=True, help=BLANK_ERROR.format("username"))
_user_parser.add_argument("password", type=str, required=True, help=BLANK_ERROR.format("password"))


class UserRegister(Resource):  # todo INFO: remember to add it as a resource
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": USERNAME_ALREADY_EXISTS.format(data["username"])}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": USER_CREATED_SUCCESSFULLY}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        return user.json() if user else {"message": USER_NOT_FOUND}, 404

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


# using flask_jwt rather than flask_jwt_extended
class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parse
        data = _user_parser.parse_args()

        # find user in database
        user = UserModel.find_by_username(data["username"])

        # check password --> this is what the 'authenticate' function used to do
        if user and hmac.compare_digest(user.password, data["password"]):
            # identity= is what the identity function used to do
            # we can use username, i.e identity=username here rather than user_id
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": INVALID_CREDENTIALS}, 401


# we should blacklist jwt, not user_id or username, except we hate that user
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        # jti >>> jwt id, unique id for jwt
        jti = get_jwt()["jti"]
        BLACKLIST_LOGOUT.add(jti)
        return {"message": SUCCESSFULLY_LOGGED_OUT}


# Doing a token refresh, NOTE parameters is refresh not fresh
# we can be sure that all token it produces are not fresh,
# Used for user who has not logged out hence we refresh their token, even after expiration
# so they don't have to keep entering their password
# so this refresh token produces an access_token which is not fresh for user to use
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
