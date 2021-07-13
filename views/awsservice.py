from flask import Blueprint, request, current_app
from libs.awsservice import *
from libs.awsclient import awsTempToken
from libs.awss3service import *
from libs.awssupport import awssupport
from libs.defResponse import success, nonauthorization
from models.Company import CompanyControl
from models.AwsTokenRecord import AwsRecordControl
from views.auth import auth
from datetime import datetime
from uuid import uuid4
import mimetypes

Awsservice = Blueprint("awsservice", __name__)

@Awsservice.route("/search", methods = ["POST"])
@auth.login_required
def search():
    if not request.json or not request.json.get("CompanyId") or not request.json.get("ServiceType") or not request.json.get("Region"): return success(20002, msg = "缺少必要参数")
    aksk = CompanyControl().getAwsSecret(request.json.get("CompanyId"))
    if not aksk: return success(20007, msg = "客户id不正确")
    data = SearchAws(request.json.get("ServiceType"), aksk[0], aksk[1], request.json.get("Region"), request.json.get("Cording", {}))
    if isinstance(data, int) and data == 401:
        return success(40001, data= [], msg = "无权限访问aws服务")
    elif isinstance(data, int) and data == 404:
        return success(40004, data= [], msg = "查询区域不存在")
    return success(data = data) if data is not  None else success(20006, msg = "服务不存在")

@Awsservice.route("/token", methods = ["POST"])
@auth.login_required
def token():
    if not request.json or not request.json.get("companyid") or not request.json.get("region"):
        return success(20003, "缺少必要参数")
    companyid  = request.json.get("companyid")
    region = request.json.get("region")
    gettime = datetime.now()
    user = auth.current_user()
    cc = CompanyControl()
    ak, sk = None, None

    if user["role"]  == "company":
        if cc.checkCompany(user["userid"], companyid):
            ak, sk = cc.getAwsSecret(companyid)
        else:
            return nonauthorization()
    elif user["role"] == 'admin' or user['role']  == 'user':
        ak, sk = cc.getAwsSecret(companyid)
    else:
        return nonauthorization()

    if not ak and not sk:
        return nonauthorization()

    args = "userid={}&companyid={}".format(user["userid"], companyid)
    saveToken = AwsRecordControl().save(user["userid"], companyid = '', getTime=gettime,
                        service="STS", operation="GentempToken", args = args)
    if not saveToken: return success(50001, "系统异常")
    token = awsTempToken(ak, sk, region)
    return success(20000, data = token)  if token else success(50001, msg = "系统异常")


@Awsservice.route("/s3upload", methods=["POST"])
@auth.login_required
def s3upload():
    if not request.json or not request.json.get("filename"): return success(20003, msg = "缺少文件名")
    userid = auth.current_user()["userid"]
    s3info = current_app.config["AWSS3INFO"]
    filename = request.json.get("filename")
    if not isinstance(filename, list): return success(20020, "数据类型错误")
    new_file = {}
    mimetypes.init()
    filedir = datetime.now().strftime("%Y-%m-%d")
    for item in filename:
        filetype = mimetypes.guess_type(item)
        new_file[item] = {
            "key": filedir + "/" +uuid4().hex+"."+item.split(".")[-1],
            "fields": {"status_action_status":"200", "Content-Type": filetype[0]} if filetype[0] else {"status_action_status": "200"},
            "conditions": [{"Content-Type": filetype[0]},{"status_action_status": "200"}]
        }
    
    gettime = datetime.now()
    args = "method=upload&bucketname={}&objectname={}".format(s3info["bucket"], filename)
    saveToken = AwsRecordControl().save(userid, companyid = '', getTime=gettime,
                        service="s3", operation="PresignUrl", args = args)

    if not saveToken: return success(50001, "系统异常")

    result = {}
    for item in new_file:
        response = awsS3PresignUrlUpload(object_name =new_file[item]["key"], fields=new_file[item]["fields"],ak = s3info["ak"], sk = s3info["sk"], bucket_name = s3info["bucket"], region = s3info["region"], conditions= new_file[item]["conditions"])
        result[item] = response
    return success(20000, data = result) if all(result) else success(50001, '系统异常')

@Awsservice.route("/servicequotacode", methods = ["POST"])
@auth.login_required
def servicequotacode():
    user = auth.current_user()
    if not request.json or not request.json.get("servicecode") or not request.json.get("companyid") or not request.json.get("region"):
        return success(20003, "缺少必要参数")
    if user["role"] == "company" and not CompanyControl().checkCompany(user["userid"], request.json.get("companyid")):
        return nonauthorization()
    saveToken = AwsRecordControl().save(user["userid"], companyid = request.json.get("companyid"), getTime=datetime.now(),
                    service="service-quota", operation="listServiceQuota", args = "servicecode="+request.json.get("servicecode"))

    if not saveToken: return success(50001, "系统异常")
    ak, sk = CompanyControl().getAwsSecret(request.json.get("companyid"))
    mm = awssupport(ak, sk, region = request.json.get("region"))
    status, data = mm.getServiceQuota(request.json.get("servicecode"))
    if status == 0:
        status = 20000
    elif status == 2:
        status == 40001
    else:
        status = 500005
    return success(status, data = data) if status == 20000 else success(status, msg = data)