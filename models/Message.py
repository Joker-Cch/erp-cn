from mongoengine import *
from uuid import uuid4
from datetime import datetime
from libs.Singleton import Singleton
class Message(DynamicDocument):
    messageid = StringField(required=True, unique=True)
    receiver = StringField(required=True)
    #等级定义： 0：system, 1:info, 2:waring, 3:stict 
    level = IntField(default=1) 
    #status: 0: not process 1: views 2: 过期
    status = IntField(default=0)
    title = StringField(required=True)
    content = StringField(required=True)
    createtime = DateTimeField(required=True)
    vailddate = DateTimeField()

    def validatestatus(self):
        if self.vailddate:
            nowdatetime = datetime.now()
            if nowdatetime> self.vailddate:
                self.status = 2
    def info(self):
        self.validatestatus()
        return {
            "messageid": self.messageid,
            "receiver": self.receiver,
            "level": self.level,
            "title": self.title,
            "status": self.status,
            "content": self.content,
            "createtime": self.createtime.strftime("%Y-%m-%d %H:%M:%S"),
            "vailddate": self.vailddate.strftime("%Y-%m-%d %H:%M:%S") if self.vailddate else None
        }
    def simpleinfo(self):
        self.validatestatus()
        return {
            "messageid": self.messageid,
            "receiver": self.receiver,
            "level": self.level,
            "title": self.title,
            "status": self.status,
            "createtime": self.createtime.strftime("%Y-%m-%d %H:%M:%S"),
            "vailddate": self.vailddate.strftime("%Y-%m-%d %H:%M:%S") if self.vailddate else None
        }

@Singleton
class MessageControl:
    def save(self, receiver, level, title, content, vaildDate):
        mid = uuid4().hex
        data = Message(messageid = mid, title = title, receiver = receiver, level = level, 
            content = content, vaildDate = vaildDate, createtime = datetime.now())
        try:
            data.save()
            return 0
        except Exception as e:
            print(e)
            return 1

    def getList(self, receiver, starttime = None, endtime = None, page = 1, pageSize = 10, sortkey = ''):
        query = Q(receiver = receiver)
        if starttime:
            query = query&Q(createtime__gte=starttime)
        if endtime:
            query = query&Q(createtime__lte=endtime)
        data = Message.objects(query).order_by(sortkey if sortkey else "-level")
        total = data.count()
        result = []
        for item in data.skip((page-1)*pageSize).limit(pageSize):
            result.append(item.simpleinfo())
        return {
            "page": page,
            "pageSize": pageSize,
            "total": total,
            "data": result
        }

    def getMessage(self,receiver, messageid):
        message = Message.objects(receiver = receiver, messageid = messageid).first()
        if message.status == 0:
            message.status = 1 
        if not message:
            return None
        else:
            message.save()
            return message.info()

    def deleteMessage(self, receiverid, message):
        result = {}
        for messageid in message:
            try:
                item = Message.objects(receiver = receiverid, messageid=messageid).first()
                if item: item.delete()
                result[messageid] = "success"
            except Exception as e:
                print(e)
                result[messageid] = "system error"
        return result

    def removeAll(self, receiverid):
        try:
            Message.objects(receiver = receiverid).delete()
            return 0
        except Exception as e:
            print(e)
            return 1