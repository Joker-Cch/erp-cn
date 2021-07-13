from mongoengine import *
from uuid import uuid4

class DataDict(DynamicDocument):
    name = StringField(required=True)
    code = StringField(required=True)
    codeid = StringField(required=True, unique=True)
    describe = StringField()
    codeclass = StringField(required=True)

    def info(self):
        return {
            "codeid": self.codeid,
            "name": self.name,
            "code": self.code,
            "describe": self.describe,
            "codeclass": self.codeclass
        }

    def getcodeclass(self):
        return self.codeclass