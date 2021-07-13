from flask import Blueprint, request
from models.DataDictSet import DataDictSetControl
from libs.defResponse import success, nonauthorization
from views.auth import auth

DataDictSetManger = Blueprint("DataDictSetManager", __name__)

allow_role = ["admin", "role"]

@DataDictSetManger.route("/dicts")
@auth.login_required(role = allow_role)
def datadictsets():
    data = request.args
    page = int(data.get("page", 1))
    page = page if page> 0 else 1
    pagesize = int(data.get("pageSize", 10))
    orderby = "-" if data.get("order", "desc") == "desc" else "+"
    sortkey = (orderby + data.get("sort")) if data.get("sort") else None
    query = data.get("query",'')
    return success(20000, data = DataDictSetControl().getDataDictSet(page, pagesize, sortkey, query))

@DataDictSetManger.route("/<datasetcode>")
@auth.login_required
def datadict(datasetcode):
    data = request.args
    page = int(data.get("page", 1))
    page = page if page> 0 else 1
    pagesize = int(data.get("pageSize", 10))
    orderby = "-" if data.get("order", "desc") == "desc" else "+"
    sortkey = (orderby + data.get("sort")) if data.get("sort") else None
    query = data.get("query",'')
    codeclass = data.get("codeclass", "")
    return success(20000, data = DataDictSetControl().getDataDict(datasetcode, page, pagesize, sortkey, query, codeclass))

@DataDictSetManger.route("/codeclass/<datasetcode>")
def datadictclass(datasetcode):
    data = request.args
    page = int(data.get("page", 1))
    page = page if page> 0 else 1
    pagesize = int(data.get("pageSize", 10))
    orderby = "-" if data.get("order", "desc") == "desc" else "+"
    sortkey = (orderby + data.get("sort")) if data.get("sort") else None
    query = data.get("query",'')
    return success(20000, data = DataDictSetControl().getDataDictSetClass(datasetcode,page, pagesize, sortkey, query))


@DataDictSetManger.route("/create", methods = ["POST"])
@auth.login_required(role = allow_role)
def dataDictSetCreate(): 
    if not request.json or not request.json.get("name") or not request.json.get("code"): return success(20003, msg = "缺少参数")
    name = request.json.get("name", "")
    describe = request.json.get("describe", "")
    code = request.json.get("code", "")
    result = DataDictSetControl().saveDataDictSet(code, name, describe)
    if result == 0:
        result = success(20000, msg = "创建成功")
    elif result == 2:
        result = success(30003, msg = "code重复")
    else:
        result = success(500001, msg = "添加失败")
    return  result

@DataDictSetManger.route("/<datasetcode>/create", methods = ["POST"])
@auth.login_required(role = allow_role)
def dataDictCreate(datasetcode):
    if not request.json : return success(20003, msg = "缺少参数")
    name = request.json.get("name")
    code = request.json.get("code")
    describe = request.json.get("describe")
    codeclass = request.json.get("codeclass")
    if not name or not code or not codeclass:
        return success(20003, msg = "缺少参数")
    result =  DataDictSetControl().saveDataDict(datasetcode, name, code, describe, codeclass)
    if result == 1:
        return success(20009, msg = "字典集不存在")
    elif result == 2:
        return success(20010, msg = "创建失败")
    else:
        return success(20000, msg = "创建成功")

@DataDictSetManger.route("/update", methods = ["POST"])
@auth.login_required(role = allow_role)
def dataDictSetUpdate():
    if not request.json: return success(20003, msg = "缺少必要参数")
    code = request.json.get("code")
    name = request.json.get("name")
    describe = request.json.get("describe")
    data = DataDictSetControl().updateDataDictSet(code, name, describe)
    if data == 1:
        return success(20009, msg = "字典集不存在")
    elif data == 2:
        return success(20004, msg = "更新失败")
    else:
        return success(20000, msg = "更新成功")

@DataDictSetManger.route("/datadict/update", methods = ["POST"])
@auth.login_required(role = allow_role)
def dataDictUpdate():
    if not request.json: return success(20003, msg = "缺少必要参数")
    codeid = request.json.get("codeid")
    code  = request.json.get("code")
    name = request.json.get("name")
    describe = request.json.get("describe")
    codeclass =  request.json.get("codeclass")
    data = DataDictSetControl().updateDataDict(codeid, name, code, describe, codeclass)
    if data == 1:
        return success(20014, msg =  "数据不存在")
    elif data == 2:
        return success(20004, msg= "更新失败")

    else:
        return success(20000, msg = "更新成功")

@DataDictSetManger.route("/delete", methods = ["POST"])
@auth.login_required(role=allow_role)
def dateDictSetDelete():
    if not request.json or not request.json.get("codes", []): return success(20003, msg="缺少参数")
    return success(20000, msg = "删除成功") if DataDictSetControl().deleteDataDictSet(request.json.get("codes", [])) else success(50005, msg = "系统异常")

@DataDictSetManger.route("/<datadictsetcode>/delete", methods = ["POST"])
@auth.login_required(role=allow_role)
def dateDictDelete(datadictsetcode):
    if not request.json or not datadictsetcode or not request.json.get("codes", []): return success(20003, msg="缺少参数")
    return success(20000, msg = "删除成功") if DataDictSetControl().deleteDataDict(datadictsetcode ,request.json.get("codes", [])) else success(50005, msg = "系统异常")