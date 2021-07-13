from flask import Blueprint, request
from models.Company import CompanyControl
from libs.defResponse import success, nonauthorization
from views.auth import auth

CompanyManange = Blueprint("CompanyManager", __name__)

@CompanyManange.route("/companys")
@auth.login_required
def companys():
    user = auth.current_user()
    data = request.args
    page = int(data.get("page", 1))
    page = page if page> 0 else 1
    pagesize = int(data.get("pageSize", 10))
    orderby = "-" if data.get("order", "desc") == "desc" else "+"
    sortkey = (orderby + data.get("sort")) if data.get("sort") else None
    query = data.get("query",'')
    managerid = data.get("managerid", None) if user["role"] !="company" else user["userid"]
    return success(20000, data = CompanyControl().getCompanys(page, pagesize, sortkey, query, managerid))

@CompanyManange.route("/add", methods = ["POST"])
@auth.login_required
def add():
    user = auth.current_user()
    if not request.json: return success(20002,msg = "无效参数")
    companyname = request.json.get("companyname")
    awsaccount = request.json.get("awsaccount")
    awsarea =  request.json.get("awsarea", "global")
    awsaccesskey  = request.json.get("awsaccesskey")
    awssecretkey = request.json.get("awssecretkey")
    contactperson = request.json.get("contactperson")
    contactphone = request.json.get("contactphone")
    contactmail = request.json.get("contactmail")
    companyinfo = request.json.get("companyinfo")
    managerid = request.json.get("managerid") if user["role"] !="company" else user["userid"]

    if not (companyname and awsaccount and awsaccesskey and awssecretkey and contactperson and  contactphone and  contactmail and managerid):
        return success(20003, msg = "无效参数")
    result = CompanyControl().addCompany(managerid, companyname, awsaccount, awsaccesskey, awssecretkey, contactperson,  contactphone, contactmail, companyinfo, awsarea)
    return success(20000, msg="添加成功") if result else success(20003, msg="添加失败")

@CompanyManange.route("/update", methods = ["POST"])
@auth.login_required
def update():
    user = auth.current_user()
    
    if not request.json and not request.json.get("companyid"): return success(20002,msg = "无效参数")
    companyid  = request.json.get("companyid")
    if user["role"] == "company" and not CompanyControl().checkCompany(user["userid"], companyid):
        return nonauthorization()
    data = request.json
    result = CompanyControl().updateCompany(companyid, data)
    return success(20000, msg="更新成功") if result else success(20003, msg="更新失败")

@CompanyManange.route("/delete", methods = ["POST"])
@auth.login_required
def delete():
    
    if not request.json or not request.json.get("company", None) or not isinstance(request.json.get("company",None), list): return success(20002,msg = "无效参数")
    dcompanys = request.json.get("company")
    data = []
    user = auth.current_user()
    if user["role"] == "company":
        for item in dcompanys:
            data.append(item) if CompanyControl().checkCompany(user["userid"], item) else None
    else:
        data=dcompanys
    return success(20000, msg="删除成功") if CompanyControl().deleteCompany(data) else success(20003, msg="删除失败")