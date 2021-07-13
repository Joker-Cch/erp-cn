from boto3 import client as awsclient
from datetime import timedelta
from time import sleep

from ..session import Session
from logger import bslog as logging
from base64 import b64decode

class Case:
    def __init__(self, path):
        self.session = Session()
        self.path = path
        self.result = {}

    def start(self):
        logging.info("任务开始:")
        task = self.gettasks()
        for item in task:
            ak, sk, token = self.token_decode(task[item]["token"])
            if not ak or  not sk or not token:
                continue
            for createitem in task[item]["tasks"].get("create"):
                status, data = self.createCase(ak, sk, token, createitem)
                self.result[createitem["caseid"]]  = {
                    "status": "created" if status else "uncreate",
                    "data": data,
                }
            data = self.queryCase(ak, sk, token, task[item]["tasks"].get("query"))
            self.result.update(data)
            #data = self.closeCase(task[item]["token"], task["item"].get("close"))
            
        status, data = self.callback()
        if status:
            logging.info(data)
        else:
            logging.error(data)
        logging.info("任务结束")
    
    def gettasks(self):
        """
        [
            "companyid":{
                token: '''
                tasks:{
                    query: [caseinfo],
                    create: [caseinfo]
                }
            }
        ]
        """
        status, data = self.session.get(self.path.get("tasks"), data = {"Page":1, "PageSize":100},timeout = 60, repeat=2)
        if not status:           
            logging.error("获取任务失败:"+data)
            logging.info("任务结束")
            exit(0)
        return data

    def callback(self):
        status, data = self.session.post(self.path.get('callback', '/task/callback'), self.result, timeout=10, repeat=3)
        return status, data

    def createCase(self, ak, sk, token, caseinfo):
        quotaclient = awsclient("service-quotas", aws_access_key_id = ak,aws_secret_access_key  = sk,  aws_session_token = token, region_name = caseinfo["region"])
        try:
            data = quotaclient.request_service_quota_increase(ServiceCode = caseinfo["servicecode"],
                QuotaCode = caseinfo["quotacode"], DesiredValue= caseinfo["desiredvalue"])
            aftertime = data["RequestedQuota"]["Created"].isoformat()
            awscase = self.findAwsCase(ak, sk, token, 'cn-north-1' if "cn" in caseinfo["region"] else "us-east-1", aftertime, caseinfo)
            return True, {
                "awscaseid": awscase["caseId"],
                "awscasedisplayid": awscase["displayId"],
                "awscasestatus": awscase["status"]
            }
        except Exception as e:
            logging.error("Create Case:"+caseinfo["caseid"]+str(e))
            return False, str(e)

    def queryCase(self, ak, sk, token, caseinfos):
        caseid = {
            "us-east-1": [],
            "cn-north-1": []
        }
        basicasemap = {}
        result = { }
        for item in caseinfos:
            if item.get("awscaseid"):
                caseid["us-east-1" if item["region"].split("-")[0] != "cn" else 'cn-north-1'].append(item["awscaseid"])
                basicasemap[item["awscaseid"]] = item["caseid"]
        for item in caseid:
            if not caseid[item]: continue
            supportclient = awsclient("support", aws_access_key_id = ak,aws_secret_access_key  = sk,  aws_session_token = token, region_name = item)
            awscases = supportclient.describe_cases(caseIdList = caseid[item])
            
            for acase in awscases["cases"]:
                result[basicasemap[acase["caseId"]]] = {
                    "status": acase["status"],
                    "data": {
                        "talk": acase.get('recentCommunications', {}).get("communications", [{}])[0].get("body")
                    }
                }
            
        return result

    def findAwsCase(self, ak, sk, token, region, aftertime, caseinfo):
        supportclient = awsclient("support", aws_access_key_id = ak,aws_secret_access_key  = sk, aws_session_token = token, region_name = region)
        nextToken = "##"
        sleep(60)
        while nextToken:            
            if nextToken == "##":
                awscases = supportclient.describe_cases(afterTime = aftertime, includeCommunications = False, includeResolvedCases= True)
            else:
                awscases = supportclient.describe_cases(afterTime = aftertime, includeCommunications = False, includeResolvedCases= True, NextToken = nextToken)
            nextToken = awscases.get("nextToken", None)
            for item in awscases["cases"]:
                if item["serviceCode"]  == "service-limit-increase":
                    return item
        return None
    
    def token_decode(self, token):
        try:
            token = "".join(token)
            token = b64decode(token.encode('utf8')).decode('utf8')
            token = token[:16]+token[48:]
            ak, token, sk = b64decode(token.encode('utf8')).decode('utf8').replace("1Q@w#e", "1_______1").replace("#1@2#3", "1_______1").split("1_______1")
            return ak, sk, token
        except Exception as e:
            logging.error(str(e))
            return None, None, None