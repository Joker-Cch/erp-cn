from flask import Blueprint, jsonify, request, current_app
from models.User import UserControl
from libs.defResponse import *
from views.auth import auth
 
UserInfo = Blueprint("UserInfo",  __name__)

@UserInfo.route("/info")
@auth.login_required
def userInfo():
    user = auth.current_user()
    return success(20000, data = UserControl().getUserInfo(user["userid"])) if user else  success(20004, msg = "无效用户")

@UserInfo.route("/checkpass", methods=["POST"])
@auth.login_required
def checkpass():
    user = auth.current_user()
    
    if not request.json: return  success(20002, msg = "无效参数")
    newpassword = request.json.get("newpassword")
    oldpassword = request.json.get("oldpassword")
    if not newpassword and oldpassword:
        return success(20002, msg = "无效参数")
    result = UserControl().checkpassword(user["userid"], oldpassword, newpassword)
    if result== 0:
        return success(20000, msg = "修改成功") 
    elif result==1:
        return success(20002, msg = "旧密码错误")
    else:
        return success(50001, msg = "系统异常")

@UserInfo.route("/update", methods = ["POST"])
@auth.login_required
def updateUser():
    user = auth.current_user()
    data = request.json
    if not data:
        return success(20003, msg="无效参数")
    return success(20000, msg = "更新成功") if UserControl().updateUser(user["userid"], data) else success(20004, msg = "更新失败")