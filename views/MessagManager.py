from flask import request, Blueprint
from views.auth import auth
from libs.defResponse import success
from models.Message import MessageControl
from datetime import datetime

MessageManager = Blueprint("MessageManager", __name__)

@MessageManager.route("/messages")
@auth.login_required
def getmessages():
    user = auth.current_user()
    page = int(request.args.get("page", 1))
    pageSize = int(request.args.get("pageSize", 10))
    orders = "-" if request.args.get("order", "desc") == "desc" else "+"
    sortkey = orders + request.args.get("sort", 'level')
    starttime = datetime.strptime(request.args.get("start"), "%Y-%m-%d %H:%M:%S") if request.args.get("start") else None
    endtime = datetime.strptime(request.args.get("end"), "%Y-%m-%d %H:%M:%S") if request.args.get("end") else None
    return success(20000, data = MessageControl().getList(user["userid"], starttime, endtime, page, pageSize, sortkey))

@MessageManager.route("/info/<messageid>")
@auth.login_required
def getmessage(messageid):
    user = auth.current_user()["userid"]
    if not messageid:
        return success(20003, msg = "缺少必要参数")
    result = MessageControl().getMessage(user, messageid)
    return success(20000, data = result) if result else success(20004, "消息不存在")

@MessageManager.route("/delete", methods = ["POST"])
@auth.login_required
def deletemessage():
    user = auth.current_user()["userid"]
    if not request.json or not request.json.get("message"): return success(20003, msg = "缺少必要参数")
    message = request.json.get("message")
    result = MessageControl().deleteMessage(user, message)
    return success(20000, data = result)

@MessageManager.route("/remove", methods = ["POST"])
@auth.login_required
def removemessage():
    user = auth.current_user()["userid"]
    return success(20000, msg = "清除成功") if MessageControl().removeAll(user) == 0 else success(20004, "清空失败")

    