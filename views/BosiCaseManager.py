from flask import Blueprint, request, current_app
from models.BosiCase import BosiCaseControl
from libs.defResponse import success, nonauthorization
from views.auth import auth
from models.Company import CompanyControl
from models.User import UserControl
from models.Message import MessageControl
from random import randint
from libs.awssupport import LambdaTaskTrigger

CaseManage = Blueprint("CaseManage", __name__)

submit_notify = """
<h3>Case：{}</h3>
尊敬的客户: <br/>
您的<a href = "/casemanage/caseinfo?caseid={}&casetype={}">case</a>已经分配处理
请留意稍后的通知
"""
assign_notify = """
<h3>Case: {}</h3>
可爱的技术人员: <br/>
有一份<a href = "/casemanage/caseinfo?caseid={}&casetype={}">case</a>需要您处理
"""
new_notify = """
<p>您的case: {} 有一条新的信息待处理</p>
"""

close_notify = """
<p>您的case: {} 已经关闭</p>
"""

def message(person, content, vailddate):
    message = MessageControl()
    message.save(person, level = 3, title = "CaseNonify", content = content, vaildDate = vailddate)

@CaseManage.route("/cases")
@auth.login_required
def cases():
    data = request.args
    page = int(data.get("page", 1))
    page = page if page> 0 else 1
    pagesize = int(data.get("pageSize", 10))
    orderby = "+" if data.get("order", "desc") == "desc" else "-"
    sortkey = (orderby + data.get("sort")) if data.get("sort") else None
    casetype = data.get("casetype")

    user = auth.current_user()
    assignperson = None
    submitperson = None
    if user["role"] == 'company':
        submitperson = user["userid"]
    elif data.get("onlyassign") == "1":
            assignperson = user["userid"]

    return success(20000, 
                data= BosiCaseControl().getCases(
                    page = page,
                    pagesize = pagesize,
                    submitperson = submitperson,
                    assignperson =  assignperson,
                    casetype = casetype,
                    sortkey = sortkey
                    ))


@CaseManage.route("/submit", methods = ["POST"])
@auth.login_required
def submit():
    if not request.json:
        return success(20003, "缺少必要参数")
    user = auth.current_user()
    companyid = request.json.get("companyid")
    techsupport = request.json.get("techsupport")
    casetype = request.json.get("casetype")
    caseinfo = request.json.get("caseinfo")
    if not (companyid and techsupport and casetype and caseinfo):
        return success(20003, "缺少必要参数")

    if user["role"].lower() == "company":
        submitperson = user["userid"]
        assignperson = UserControl().getCaseAssginUser()
        assignperson = assignperson[randint(0, len(assignperson)-1)]   
        if not CompanyControl().checkCompany(submitperson, companyid):
            return success(40001, "非法Case,无权限给此公司提交case")
    else:
        submitperson = request.json.get("submitperson")
        assignperson = user["userid"]
    status, result = BosiCaseControl().saveCase(submitperson, assignperson, companyid, techsupport, casetype, caseinfo)
    if status == 20000:
        message(submitperson, submit_notify.format(result, result, casetype),None )
        message(assignperson, assign_notify.format(result, result, casetype), None)
        LambdaTaskTrigger(current_app.config.get("LAMBDATASK_AK", None),
            current_app.config.get("LAMBDATASK_SK", None)).enabled(
                current_app.config.get("LAMBDATASK_EVENTNAME", 'BosiCaseCrontab'),
                current_app.config.get("LAMBDATASK_EVENTBUS", 'default'))
    return success(status , msg = result) if status !=20000 else success(status, data = result)

@CaseManage.route("/caseinfo")
@auth.login_required
def caseinfo():
    data = request.args if request.args else {}
    print(request.data)
    caseid = data.get("caseid")
    casetype = data.get("casetype")
    user = auth.current_user()
    submitperson = user["userid"] if user["role"] == "company" else None
    status, result = BosiCaseControl().getCaseInfo(caseid, casetype, submitperson)
    return success(status, data = result if status == 20000 else '', msg = result if status != 20000 else '')

@CaseManage.route("/casetalk/save", methods = ["POST"])
@auth.login_required
def casetalkSave():
    bsc = BosiCaseControl()
    caseid = request.json.get("caseid")
    if not caseid:
        return success(20003, "缺少caseid")
    caseperson = bsc.getCasePerson(caseid)
    content = request.json.get("content")
    if not content:
        return success(20003, "会话内容为空")
    user = auth.current_user()
    if user["role"] == "company" and user["userid"] != caseperson["submit"]:
        return nonauthorization()
    status, casetalk = bsc.saveCaseTalk(caseid, user["userid"], content, user["role"])
    if not status:
        return success(50001, casetalk)
    for item in caseperson.values():
        if item != user["userid"]:
            message(item, new_notify.format(caseid),None)
    return success(20000, casetalk) 
    
@CaseManage.route("/casetalk")
@auth.login_required
def casetalkList():
    if not request.args and request.args.get("caseid"): return success(20003, "缺少必要参数")
    caseid = request.args.get("caseid")
    start = request.args.get("start")
    end = request.args.get("end")
    status, result = BosiCaseControl().getCaseTalk(caseid, start, end)
    return success(20000, data = result) if status else success(20003, msg = result)
    
@CaseManage.route("/closeCase", methods = ["POST"])
@auth.login_required
def caseClose():
    if not request.json.get("caseid"):
        return success(20003, "缺少caseid")
    user = auth.current_user()
    caseid = request.json.get("caseid")
    if user["role"] == "company":
        if not BosiCaseControl().checkCase(caseid, user["userid"]):
            return nonauthorization()
    status, result = BosiCaseControl().updateCaseStatus(caseid, "close")
    if status == 20000:
        caseperson = BosiCaseControl().getCasePerson(caseid)
        for item in caseperson.values():
            
            message(item, close_notify.format(caseid),None)
        result = "CASE: {} 已关闭".format(caseid)
    return success(status, msg= result)