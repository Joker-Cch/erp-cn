from flask import Blueprint, jsonify, request, current_app
from models.User import UserControl
from libs.defResponse import *
from views.auth import auth
allow_role = ["admin"]
UserManager = Blueprint("UserManager",  __name__)
@UserManager.route("/users")
@auth.login_required(role=["admin", "user"])
def UserList():
    data = request.args
    page = int(data.get("page", 1))
    page = page if page> 0 else 1
    pagesize = int(data.get("pageSize", 10))
    orderby = "-" if data.get("order", "desc") == "desc" else "+"
    sortkey = (orderby + data.get("sort")) if data.get("sort") else None
    query = data.get("query",'')
    role = data.get("role", None)
    data = UserControl().getUsers(page, pagesize, sortkey, query, role)
    return success(20000, data =  data)

@UserManager.route("/getCustom")
@auth.login_required(role=["username", "admin"])
def CompanyList():
    return success(20000, UserControl().getCompanylist())

@UserManager.route("/deleteusers", methods = ["POST"])
@auth.login_required(role=allow_role)
def deleteUser():
    userid = request.json.get("user")
    if not userid and not isinstance(request.json.get("user"), list):
        return success(20002,msg = "无效参数")
    return success(msg = "删除成功") if UserControl().deleteUser(userid) else success(msg = "删除出错")

@UserManager.route("/adduser", methods = ["POST"])
@auth.login_required(role=allow_role)
def addUser():
    data = request.json
    if not data: return success(20002, msg="无效参数")
    username = data.get("username")
    name = data.get("name")
    password = data.get("password")
    mail = data.get("mail")
    phone  = data.get("phone")
    role = data.get("role", 'user')
    info = data.get("info", "")
    if not (username or password or mail or name or phone): return success(20002, msg="无效参数")
    status = UserControl().addUser(username, mail, password, phone, name, role, info)
    return success(20000, msg= "添加成功") if status else success(20004, msg = "添加失败")

@UserManager.route("/checkpass", methods = ["POST"])
@auth.login_required(role=allow_role)
def checkpass():
    data = request.json
    userid = data.get("userid")
    newpassword = data.get("newpassword")
    if not userid and not newpassword:
        return success(20002, msg="无效参数")    
    
    result = UserControl().checkpassword(userid, "", newpassword, admin = True)
    if result== 0:
        return success(20000, msg = "修改成功") 
    else:
        return success(50001, msg = "系统异常")

@UserManager.route("/userinfo", methods = ["POST"])
@auth.login_required(role=allow_role)
def Userinfo():
    if not (request.json  and request.json.get("userid")):
        return success(20002, msg="无效参数")   
    user = UserControl().getUserInfo(request.json.get("userid"))
    return success(20000, data = user) if user else success(20003, msg="用户不存在")

@UserManager.route("/stopuser", methods = ["Post"])
@auth.login_required(role = allow_role)
def stopuser():
    if not (request.json and request.json.get("user") and isinstance(request.json.get("user"), list)):
        return success(20002, msg="无效参数")
    result = {}
    data = {
            "status": False
        }
    for item in request.json.get("user"):
        result[item] = UserControl().updateUser(item, data)
            
    return success(20000, data = result)

@UserManager.route("/startuser", methods = ["POST"])
@auth.login_required(role = allow_role)
def startuser():
    if not (request.json and request.json.get("user") and isinstance(request.json.get("user"), list)):
        return success(20002, msg="无效参数")
    result = {}
    data = {
            "status": True
        }
    for item in request.json.get("user"):
        
        result[item] = UserControl().updateUser(item, data)
            
    return success(20000, data = result)
