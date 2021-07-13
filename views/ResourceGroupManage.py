from flask import Blueprint, jsonify, request
from models.ResourceGroup import ResourceGroupControl
from models.Company import CompanyControl
from libs.defResponse import *
from views.auth import auth

RGManage = Blueprint("RGManage", __name__)

@RGManage.route("/groups")
@auth.login_required
def groups():
    user = auth.current_user()
    page = 1
    pagesize = 10
    sortkey=None
    query = ""
    companyid = None
    region = None
    envname = None
    serviceType = None
    if request.args:
        try:
            page = int(request.args.get("page", 1))
            pagesize = int(request.args.get("pageSize", 10))
        except:
            return success(20008, msg = "page, pagesiZe为整数类型")
        order = "-" if request.args.get("order", "desc") == "desc" else "+"
        sortkey = order+request.args.get("sort") if request.args.get("sort") else None
        query = request.args.get("query", '')
        companyid = request.args.get("companyid")
        envname = request.args.get("envname")
        region = request.args.get('region')
        serviceType = request.args.get("serviceType")

    if user["role"] == "company":
        if companyid:
            if not CompanyControl().checkCompany(user["userid"], companyid):
                return nonauthorization()

        else: 
            companys = CompanyControl().getCompanys(pagesize = 1000, managerid = user["userid"])["data"]
            if not companys:
                return success(20000, {
                            "page": page,
                            "pageSize": pagesize,
                            "total": 0,
                            "data": []
                        })
            companyid = [item["companyid"] for item in companys]

    if not isinstance(companyid, list) and companyid: companyid = [companyid]
    return success(20000, ResourceGroupControl().getRGlist(page, pagesize, sortkey, query, companyid, region, envname, serviceType))

@RGManage.route("/groupinfo")
@auth.login_required
def groupinfo():
    data = request.args
    if not data and data.get("groupid"): return success(20002, msg = "缺少groupid")
    data = ResourceGroupControl().getRG(data["groupid"])
    user = auth.current_user()
    if user["role"] == "company" and not CompanyControl().checkCompany(user["userid"], data["companyid"]):
        return nonauthorization()
    return success(20000, data) if data else success(20003, "无效资源组")

@RGManage.route("/add", methods = ["POST"])
@auth.login_required
def addRG():

    createauthorid = auth.current_user()["userid"]
    userrole = auth.current_user()["role"]
    data = request.json
    if not data: return success(20002, msg = "无效参数")
    groupname = data.get("groupname")
    envname = data.get("envname")
    companyid = data.get("companyid")
    region = data.get("region")
    servicetype = data.get("serviceType")
    resource = data.get("resource")
    print(userrole)
    if userrole=="company" and not CompanyControl().checkCompany(createauthorid, companyid):
        return nonauthorization()
    return success(20000, msg = "添加成功") if ResourceGroupControl().addRG(companyid, createauthorid,
        groupname, envname, region, servicetype, resource) else success(20004, msg = "添加失败")

@RGManage.route("/update", methods=["POST"])
@auth.login_required
def updateRG():
    data = request.json
    if not data:  return success(20002, msg="无效参数")
    groupid = data.get("groupid")
    groupname = data.get("groupname")
    envname = data.get("envname")
    resource = data.get("resource")
    if not groupid: return success(20002, msg = "缺少groupid")
    data = ResourceGroupControl().getRG(groupid)
    if not data:
        return success(20002, msg="无效参数")
    user = auth.current_user()
    if user["role"] == "company" and not CompanyControl().checkCompany(user["userid"], data["companyid"]):
        return nonauthorization()
    result = ResourceGroupControl().updateRG(groupid, groupname, envname, resource)
    print(result)
    if result==2:
        result = success(20002, msg="无效参数")
    elif result== 1:
        result = success(50001, msg="系统异常")
    else:
        result = success(20000, msg = "更新成功")

    return result


@RGManage.route("/delete", methods = ["POST"])
@auth.login_required
def deleteRG():
    data = request.json
    if not data or not data.get("group") or not isinstance(data.get("group"), list): return success(20000, "无效参数")
    dgroup = []
    for item in data.get("group"):
        item = ResourceGroupControl().getRG(item)
        user = auth.current_user()
        if not item or (user["role"] == "company" and not CompanyControl().checkCompany(user["userid"], item["companyid"])):
            continue
        else:
            dgroup.append(item["groupid"])
    

    return success(20000, msg = "删除成功") if ResourceGroupControl().deleteRG(dgroup) else success(20004, msg = "删除失败")



