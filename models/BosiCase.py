from mongoengine import  *
from uuid import uuid4
from datetime import datetime
from libs.Singleton import Singleton
from flask.logging import logging
from flask import current_app
from models.User import UserControl
from models.Company import CompanyControl
from libs.awssupport import awssupport
from libs.awsclient import awsTempToken
from libs.awss3service import awsS3PresignUrlDownload

class BosiCase(DynamicDocument):
    caseid = StringField(required=True, unique=True)
    submitperson = StringField(required=True)
    assignperson = StringField(required=True)
    companyid = StringField(required=True)
    techsupport = StringField(required=True)
    awscaseid = StringField()
    awscasedisplayid = StringField()
    casetype = StringField(required=True)
    casestatus = StringField(default="wait")
    createdate = DateTimeField(required=True)
    def info(self):
        companyname = CompanyControl().getCompanyName(self.companyid)
        users = UserControl()
        submitpersonname = users.getUserInfo(self.submitperson)
        assignpersonname = users.getUserInfo(self.assignperson)
        return {
            "caseid": self.caseid,
            "submitperson": self.submitperson,
            "submitpersonname": "{}({})".format(submitpersonname["username"], submitpersonname["name"]) if submitpersonname else "",
            "assignperson": self.assignperson,
            "assignpersonname": "{}({})".format(assignpersonname["username"], assignpersonname["name"]) if assignpersonname else "",
            "companyid": self.companyid,
            "companyname": companyname if companyname else "",
            "techsupport": self.techsupport,
            "awscaseid": self.awscaseid,
            "awscasedisplayid": self.awscasedisplayid,
            "casetype": self.casetype,
            "casestatus": self.casestatus,
            "createdate": self.createdate.strftime("%Y-%m-%d %H:%M:%S")
        }

class CaseInfo(DynamicDocument):
    caseid = StringField(required=True)
    title = StringField(required=True)
    importance = StringField(required=True)
    attachments = ListField(StringField())
    casedescribe = StringField()
    def info(self):
        s3info = current_app.config.get("AWSS3INFO", {})
        outattachments = []
        if self.attachments:
            for item in self.attachments:
                outattachments.append(awsS3PresignUrlDownload(s3info["ak"], s3info["sk"], bucket_name = s3info["bucket"], region = s3info["region"], object_name = item))
        return {
            #"caseid": self.caseid,
            "title": self.title,
            "importance": self.importance,
            "attachments": outattachments,
            "casedescribe": self.casedescribe
        }

class ServiceQuotaCase(DynamicDocument):
    caseid = StringField(required=True)
    region = StringField(required=True)
    servicecode = StringField(required=True)
    quotacode = StringField(required=True)
    desiredvalue = IntField(required=True)

    def info(self):
        return {
            #"caseid": self.caseid,
            "region": self.region,
            "servicecode": self.servicecode,
            "quotacode": self.quotacode,
            "desiredvalue": self.desiredvalue
        }

"""{'RequestedQuota': {'Id': 'c061983feeda4076921a8716edb99c8cjCWBA7U9', 'ServiceCode': 'ec2', 'ServiceName': 'Amazon Elastic Compute Cloud (Amazon EC2)', 'QuotaCode': 'L-0263D0A3', 'QuotaName': 'Number of EIPs - VPC EIPs', 'DesiredValue': 6.0, 'Status': 'PENDING', 'Created': datetime.datetime(2020, 8, 10, 13, 58, 16, 37000, tzinfo=tzlocal()), 'Requester': '{"accountId":"917958955567","callerArn":"arn:aws:iam::917958955567:user/chaojie.chen@bosicloud.com"}', 'QuotaArn': 'arn:aws:servicequotas:ap-southeast-1:917958955567:ec2/L-0263D0A3', 'GlobalQuota': 
False, 'Unit': 'None'}, 'ResponseMetadata': {'RequestId': '3498fa8c-0103-461c-84c1-0d1d66b5f138', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Mon, 10 Aug 2020 05:58:16 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '511', 'connection': 'keep-alive', 'x-amzn-requestid': '3498fa8c-0103-461c-84c1-0d1d66b5f138'}, 'RetryAttempts': 0}}"""

class CaseTalk(DynamicDocument):
    caseid = StringField(required=True)
    whosaid = StringField(required=True)
    content = StringField(required=True)
    createtime = DateTimeField(required=True)

    def info(self):
        users =UserControl()
        personname = users.getUserInfo(self.whosaid) if self.whosaid != "aws" else {"username":"AWS", "name":"AWS Support"}
        return {
            #"caseid": self.caseid,
            "whosaid": self.whosaid,
            "personname":  "{}({})".format(personname["username"], personname["name"]) if personname else "",
            "content": self.content,
            "createtime": self.createtime.strftime("%Y-%m-%d %H:%M:%S")
        }

@Singleton
class BosiCaseControl:
    def saveCase(self, submitperson, assignperson, companyid, techsupport, casetype, caseinfo):
        casedate = self.gencreateDate()
        caseid = self.genCaseId(casedate)
        if casetype == "TechCase":
            caseinfo = self.saveCaseInfo(caseid, caseinfo)
        elif casetype == "ServiceQuota":
            caseinfo = self.saveServiceQuotaCase(caseid, caseinfo)
        else:
            return 20003, "不受支持的Case类型"
        if caseinfo == 1:
            return 20003, "Case详情参数不正确"
        elif caseinfo == 2:
            return 50001, "系统异常"
        
        case = BosiCase(caseid = caseid, 
                        submitperson =submitperson,
                        assignperson =assignperson,
                        companyid =companyid,
                        techsupport =techsupport,
                        casetype =casetype,
                        createdate = casedate)
        try:
            case.save()
            return 20000,caseid
        except Exception as e:
            logging.error(str(e))
            caseinfo.delete()
            return 50001, "系统异常"
    
    def saveCaseInfo(self, caseid, caseinfo):
        title = caseinfo.get("Title")
        importance  = caseinfo.get('Importance')
        attachments = caseinfo.get("Attachments")
        casedescribe = caseinfo.get("Describe")
        if not title or not importance:
            return 1
        try:
            caseinfo = CaseInfo(caseid = caseid,title = title, importance = importance,  attachments = attachments, casedescribe = casedescribe)
            caseinfo.save()
            return caseinfo
        except Exception as e:
            logging.error(str(e))
            return 2
    
    def saveServiceQuotaCase(self, caseid, caseinfo):
        servicecode = caseinfo.get("ServiceCode")
        quotacode = caseinfo.get('QuotaCode')
        region = caseinfo.get("Region")
        try:
            desiredvalue = int(caseinfo.get("DesiredValue"))
        except:
            return 1
        if not (servicecode and  quotacode and desiredvalue and region):
            return 1
        try:
            caseinfo = ServiceQuotaCase(caseid = caseid, servicecode = servicecode, quotacode = quotacode, desiredvalue = desiredvalue, region = region)
            caseinfo.save()
            return caseinfo
        except Exception as e:
            logging.error(str(e))
            return 2

    def saveCaseTalk(self, caseid, whosaid, content, role):
        bs =  BosiCase.objects(caseid = caseid).first()
        try:
            if role != "company":
                bs.casestatus = "reply"
            else:
                bs.casestatus = "process"
            bs.save()
        except Exception as e:
            logging.error(str(e))
            return False, "系统异常"
        if CaseTalk.objects(caseid = caseid, whosaid = whosaid, content= content).first():
            return True, "消息已经存在"
        casetalk = CaseTalk(caseid = caseid, whosaid = whosaid, content = content, createtime = datetime.now())
        try:
            casetalk.save()
            return True, "保存成功"
        except Exception as e:
            logging.error(str(e))
            return False, "系统异常"

    def getCases(self, page=1, pagesize=10,  submitperson = None, assignperson = None, casetype = None, sortkey=None):
        query = None
        if submitperson:
            query = Q(submitperson=submitperson)
        if assignperson:
            query = Q(assignperson= assignperson) if not query else query&Q(assignperson= assignperson)
        if casetype:
            query = Q(casetype= casetype) if not query else query&Q(casetype= casetype)
        sortkey = "-createdate" if not sortkey else sortkey
        cases = BosiCase.objects(query).order_by(sortkey) if query else BosiCase.objects().order_by(sortkey)
        total = cases.count()
        result = []
        for item in cases.skip((page-1)*pagesize).limit(pagesize):
            result.append(item.info())
        return {
            "page": page,
            "pageSize": pagesize,
            "total": total,
            "data": result
        }

    def getCaseInfo(self, caseid, casetype, submitperson = None, assignperson = None):
        if not caseid or not casetype:
            return 20003, "缺少必要参数"
        else:
            query = Q(caseid = caseid)&Q(casetype = casetype)
        if submitperson:
            query = Q(submitperson=submitperson)&query
        if assignperson:
            query = query&Q(assignperson= assignperson)
        case = BosiCase.objects(query).first()
        if not case:
            return 40004, "Case不存在"
        case = case.info()
        caseinfo = ServiceQuotaCase.objects(caseid = caseid).first().info() if casetype == "ServiceQuota" else CaseInfo.objects(caseid = caseid).first().info()
        case["caseinfo"] = caseinfo
        casetalk = CaseTalk.objects(caseid = caseid).order_by("-createtime").all()
        case["casetalk"] = [item.info() for item in casetalk] if casetalk else []

        return 20000, case

    def getCasePerson(self, caseid):
        case = BosiCase.objects(caseid = caseid).first()
        return {
            "submit": case.submitperson,
            "assgin": case.assignperson
        }

    def getCaseTalk(self, caseid, start, end, nums = 1):
        query = Q(caseid = caseid)
        try:
            if start:
                start =  datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                query = query|Q(createtime__gte=start)
            if end:
                end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                query = query|Q(createtime__lte=end)
        except:
             return False, "不正确时间格式"
        casetalks = CaseTalk.objects(query).order_by("-createtime").limit(nums)
        return True, [item.info() for item in casetalks]

    def updateCaseStatus(self, caseid, status):
        case = BosiCase.objects(caseid = caseid).first()
        if not caseid:
            return 20004, "Case不存在"
        case.casestatus = status
        try:
            case.save() 
            return 20000, "更新成功"
        except Exception as e:
            logging.error(str(e))
            return 50001, "系统异常"

    def updateCaseAwscaseid(self, caseid, awscaseid, awscasedisplayid):
        if not awscaseid and not awscasedisplayid:
            return False, "缺少awscaseid, awscasedispalyid"
        case = BosiCase.objects(caseid = caseid).first()
        if not case:
            return False, "Case不存在"
        try:
            case.awscaseid = awscaseid
            case.awscasedispalyid = awscasedisplayid
            case.save()
            return True, "更新成功"
        except Exception as e:
            return False, "系统异常"

    def checkCase(self, caseid, submitperson):
        case = BosiCase.objects(caseid = caseid, submitperson= submitperson).first()
        return True if case else False

    def genCaseId(self, createtime):
        casedate = str(createtime).split(" ")[0].replace("-", "")
        return casedate+uuid4().hex[:10]
    
    def gencreateDate(self):
        return datetime.now()

    def getCaseTask(self):
        casestatus = {}
        result = {}
        caseset = BosiCase.objects(casestatus__ne = "close", casetype = "ServiceQuota")
        tasknums = caseset.count()
        for item in caseset.all():
            if not result.get(item.companyid):
                result[item.companyid]  = {
                    "tasks": {
                        "create": [],
                        "query": []
                    }
                }
            caseinfo = ServiceQuotaCase.objects(caseid = item.caseid).first()
            if item.casestatus == "wait":
                
                result[item.companyid]["tasks"]["create"].append({
                    "caseid": caseinfo.caseid,
                    "region": caseinfo.region,
                    "servicecode": caseinfo.servicecode,
                    "quotacode": caseinfo.quotacode,
                    "desiredvalue": caseinfo.desiredvalue
                })
            elif item.casestatus == "proccess":
                result[item.companyid]["tasks"]["query"].append({
                    "caseid": item.caseid,
                    "region": caseinfo.region,
                    "awscaseid": item.awscaseid,

                })
        for item in result.keys():
            ak,sk = CompanyControl().getAwsSecret(item)
            token =  awsTempToken(ak, sk, 'ap-southeast-1')
            if not token:
                result.popitem(item)
                logging.error("companyid: {}, aksk凭证无效")
            result[item]["token"] = [token[item*128:(item+1)*128] for item in range((len(token)//128)+1)]
        return tasknums, result

    def updateByCallBack(self, data):
        if not isinstance(data, dict): return False, "不正确数据格式"
        for item in data:
            bscase = BosiCase.objects(caseid = item).first()
            if data.get(item).get("status") == "uncreate":
                continue
            if data[item]["data"].get("awscaseid"):
                if data.get(item).get("status") == 'created':
                    bscase.awscaseid = data[item]["data"]["awscaseid"]
                    bscase.awscasedisplayid = data[item]["data"]["awscasedisplayid"]
                    bscase.casestatus = "proccess"
            else:
                if data[item].get("status") == "resolved":
                    bscase.casestatus = "close"
                elif data[item].get("status") == "pending-customer-action":
                    bscase.casestatus = "reply"
                if data[item]["data"].get("talk"):
                    if not CaseTalk.objects(caseid = item, whosaid = "aws", content =str(data[item]["data"].get("talk"))).first():
                    
                        ct = CaseTalk(caseid = item, whosaid = "aws", content = str(data[item]["data"].get("talk")), createtime = datetime.now())
                        try:
                            ct.save()
                        except Exception as e:
                            logging.error(e)
            bscase.save()
        tasknums = BosiCase.objects(casestatus__ne = "close", casetype = "ServiceQuota").count()
        return True, tasknums