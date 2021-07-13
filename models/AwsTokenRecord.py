from mongoengine import *
from uuid import uuid4
from datetime import datetime

class AwsTokenRecord(DynamicDocument):
    userid = StringField(required=True)
    companyid = StringField()
    getTime = DateTimeField(required=True)
    service = StringField(required=True)
    operation = StringField()
    args = StringField()

class AwsRecordControl:
    def save(self, userid, companyid, getTime, service, operation, args):
        data = AwsTokenRecord(userid = userid, companyid = companyid, getTime = getTime, service = service, operation=operation, args = args)
        try:
            data.save()
            return True
        except Exception as e:
            print(e)
            return False