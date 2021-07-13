from flask import current_app, request, Blueprint
from models.User import UserControl
from models.Token import Token
from libs.defResponse import *
from hashlib import sha256
from flask_httpauth import HTTPTokenAuth
import time

auth = HTTPTokenAuth(scheme="Bosi")
tokenmananger = Token()

@auth.verify_token
def vaildToken(token):
    if not token: return None
    user = tokenmananger.getToken(token)
    return user

@auth.get_user_roles
def get_user_roles(user):
    return [user.get("role")]

@auth.error_handler
def nonauthority(error):
    return {
        "status": 40001,
        "msg": "身份未验证",
        "data": ""
    }

Auth = Blueprint("Auth", __name__)
@Auth.route("/login", methods = ["POST"])
def login():
    """
    swagger_from_file: login.yml
    """
    if not request.json: return success(20002, data = "", msg ="无效参数")
    username = request.json.get("username")
    password = request.json.get("password")
    if not username or not password:
        return success(20002, data = "", msg ="无效参数")
    user = UserControl().loginUser(username, password)
    if not user:
        return success(20003, data = "", msg = "无效用户")
    token = tokenmananger.genToken(user["userid"], user["role"])
    user.update(token)
    return success(20000, data=user, msg="")

@Auth.route("/logout")
@auth.login_required
def logout():
    user = auth.current_user()
    print(user)
    tokenmananger.delToken(user["token"])
    return success(20000, data="", msg="登出")