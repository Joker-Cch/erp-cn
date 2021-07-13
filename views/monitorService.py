from flask import Blueprint, request
from views.auth import auth
from models.MonitorService import MonitorServiceControl
from libs.defResponse import success, nonauthorization

monitorServiceView = Blueprint("monitorServiceView", __name__)
managerrole = ["admin", "user"]

@monitorServiceView.route("/serviceconfig")
@auth.login_required(role = managerrole)
def getconfig():
    status, data = MonitorServiceControl().get_config(
        customer = request.args.get("customer")
    )
    return success(status, data = data) if status==20000 else success(status, msg= data)
    e
@monitorServiceView.route("/services")
@auth.login_required
def gets():
    try:
        page = int(request.args.get("page", '1'))
    except:
        page = 1
    try:
        pagesize = int(request.args.get("pageSize", 10))
    except:
        pagesize = 10
    orderby = "-" if request.args.get("order", "desc") == "desc" else "+"
    sortkey = (orderby + request.args.get("sort")) if request.args.get("sort") else None
    customerid = request.args.get("customerid")
    cloudaccountid = request.args.get("cloudaccount")
    business = request.args.get("business")
    user = auth.current_user()
    if user["role"]== "company":
        customerid = user["userid"]
    return  success(20000, data = MonitorServiceControl().gets(page, pagesize, sortkey, customerid, cloudaccountid, business))

@monitorServiceView.route("/service/<msid>")
@auth.login_required
def getitem(msid):
    if not msid: return success(20003, "缺少必要参数")
    user = auth.current_user()
    if user["role"] == "company" and not MonitorServiceControl().checkaccess(msid, user["userid"]):
        return nonauthorization()
    result = MonitorServiceControl().getitem(msid)
    return success(20000 if result else 20003, data = result if result else "",  msg = "无效id" if not result else '')

@monitorServiceView.route("/add", methods = ["POST"])
@auth.login_required(role = managerrole)
def add():
    if not request.json: return success(20003, msg = "缺少参数")
    if not (request.json.get("msname") and request.json.get("customer") and \
        request.json.get("cloudaccount") and  request.json.get("monitorperiod") and \
            request.json.get("monitorgroup") and request.json.get('business') and \
                request.json.get("monitorenv") and request.json.get("monitorarea") and request.json.get("reportpersonid")):
        return success(20003, msg= "缺少必要参数")

    if not isinstance(request.json.get("monitorgroup"), list) or not isinstance(request.json.get("monitorgroup", [1])[0], dict):
        return success(20003, msg = "监控指标数据类型异常，应为list(dict)")
    groups = [  item 
                for item in request.json.get("monitorgroup") 
                if item.get("mgname") and item.get("servicetype") and item.get("resourcegroup") and item.get("metrics")
    ]
    if not groups: return success(20003, msg = "监控指标数据类型异常,子项为dict,必须键值为mgname, servicetype,resource, metrics")
    
    status, result = MonitorServiceControl().add(
        request.json.get("msname"),
        request.json.get("customer"),
        request.json.get("cloudaccount"),
        request.json.get("business"),
        request.json.get("monitorperiod"),
        request.json.get("monitorenv"),
        request.json.get("monitorarea"),
        request.json.get("reportpersonid"),
        groups
    )
    if status:
        return success(20000, data= result[1], msg = result[0])
    else:
        return success(50001, msg = result)

@monitorServiceView.route("/delete", methods= ["POST"])
@auth.login_required(role = managerrole)
def delete():
    if not request.json or not request.json.get("msids"):
        return success(20003, "缺少必要参数")
    if not isinstance(request.json.get("msids"), list):
        return success(20004, "数据类型不对，应为list")
    return success(20000, data = MonitorServiceControl().delete(request.json.get("msids")))

@monitorServiceView.route("/update", methods = ["POST"])
@auth.login_required(role = managerrole)
def update():
    if not request.json or not request.json.get("msid"):
        return success(20003, msg = '未指定更新的服务')
    if not request.json.get("data"):
        return success(20003, msg = "更新内容为空")
    else:
        data = request.json.get("data")
    if not isinstance(data, dict):
        return success(20050, msg = "更新内容数据异常")
    if data.get("monitorgroup") and not isinstance(data.get('resourcegroup'),list):
        return success(20051, msg= "监控组信息异常")
    if not data.get("monitorgroup"):
        return success(200052, msg= "监控组组必须配置")
    status, result = MonitorServiceControl().update(
        request.json.get("msid"), 
        data.get("msname", None),
        data.get("customer", None),
        data.get("cloudaccount", None),
        data.get("business", None),
        data.get("monitorperiod", None),
        data.get("monitorgroup", [])
    )
    return success(result[0], msg = result[1])                                                                                                                            