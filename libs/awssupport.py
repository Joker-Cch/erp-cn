from libs.awsclient import awsclient
from flask.logging import logging
from botocore.exceptions import ClientError 
from json import dumps as json_dumps

class awssupport:
    def __init__(self, ak = None, sk = None, region="us-east-1"):
        self.supportclient = self.supportclient(ak, sk, region)
        self.quotaclient = self.quotaClient(ak, sk, region)
    def supportclient(self, ak, sk, region):
        if region:
            if "cn-north" in region:
                region = "cn-north-1"
            else:
                region = "us-east-1"
        return awsclient("support", ak, sk, region)
    
    def quotaClient(self, ak, sk, region):
        return awsclient("service-quotas",ak, sk, region)

    def getcasestatus(self):
        pass
    def createcase(self):
        pass

    def increaseServiceQuota(self):
        pass

    def getServiceQuota(self, servicecode):
        try:
            data = self.quotaclient.list_service_quotas(ServiceCode=servicecode)
            result = [ {"QuotaCode": item["QuotaCode"], "QuotaName":item["QuotaName"], "Value": item["Value"]} for item in data["Quotas"]]
            nexttoken = data["NextToken"]
            while nexttoken:
                data = self.quotaclient.list_service_quotas(ServiceCode=servicecode, NextToken = nexttoken)
                result + [ {"QuotaCode": item["QuotaCode"], "QuotaName":item["QuotaName"], "Value": item["Value"] } for item in data["Quotas"]]
                nexttoken = data.get("NextToken")
            return 0, result
                
        except ClientError as e:
            logging.error(str(e))
            return 1,  "凭证错误"
        except Exception as e:
            logging.error(str(e))
            return 2, "未知异常"

class LambdaTaskTrigger:
    def __init__(self, ak, sk, region = 'ap-southeast-1'):
        self.client = awsclient("events", ak, sk, region = region)

    def enabled(self, eventname, eventbus = "default"):
        while True:
            try:
                self.client.enable_rule(Name = eventname, EventBusName = eventbus)
                return True
            except ClientError as e:
                logging.error(str(e))
            except Exception as e:
                logging.error(str(e))
                break
        return False
    
    def disabled(self, eventname, eventbus = "default"):
        while True:
            try:
                self.client.disable_rule(Name = eventname, EventBusName = eventbus)
                return True
            except ClientError as e:
                logging.error(str(e))
            except Exception as e:
                logging.error(str(e))
                break
        return False
            
    
# def readservice():
#     mm = client("service-quotas")
#     nexttoken = True
#     result = []
#     with open('listservice', 'w+', encoding='utf8') as f:
#         while nexttoken:
#             if isinstance(nexttoken, str):
#                 data = mm.list_services(NextToken=nexttoken)
#             else:
#                 data = mm.list_services()
#             nexttoken = data.get("NextToken", None)
#             result = result+ data["Services"]
#     return result

# map

"""
from libs.awssupport import awssupport
mm = awssupport(region= "ap-southeast-1")
data = mm.getServiceQuota("ec2")
"""