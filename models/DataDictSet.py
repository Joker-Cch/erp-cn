from mongoengine import *
from uuid import uuid4
from models.DataDict import DataDict
from libs.Singleton import Singleton

class DataDictSet(DynamicDocument):
    name = StringField(required=True, unique=True)
    code = StringField(required=True)
    describe  = StringField()
    datadict = ListField(LazyReferenceField(DataDict))

    def info(self):
        return {
            "code": self.code,
            "name": self.name,
            "describe": self.describe,
            "datadictnums": len(self.datadict)
        }

@Singleton
class DataDictSetControl:
    def __init__(self):
        self.cache = {}
    def saveDataDictSet(self, code, name, describe):
        if DataDictSet.objects(code = code).first():
            return 2
        data = DataDictSet(code  = code, name = name, describe = describe)
        try:
            data.save()
            return 0
        except Exception as e:
            print(e)
            return 1
    
    def saveDataDict(self, datadictsetcode, name, code, describe, codeclass):
        datadictset = DataDictSet.objects(code = datadictsetcode).first()
        if not datadictset:
            return 1
        data = DataDict(codeid=uuid4().hex, name=name, code=code, describe = describe, codeclass = codeclass)
        try:
            data.save()
        except Exception as e:
            print(e)
            return 2
        datadictset.datadict.append(data)
        try:
            datadictset.save()
            if self.cache.get(datadictsetcode):
                self.cache[datadictsetcode].append(data.info())
            return 0
        except Exception as e:
            print(e)
            data.delete()
            return 3
    
    def getDataDictSet(self, page = 1, pageSize = 10, sortkey = "", query= ""):
        if query: 
            query = Q(name__icontains = query)|Q(describe__icontains = query)
        else:
            query = None
        datadictset = DataDictSet.objects(query)
        
        datadictset = datadictset.order_by(sortkey if sortkey else "name")
        datadictset = datadictset.skip((page-1)*pageSize).limit(pageSize)
        total = datadictset.count()
        data = []
        for item in datadictset:
            data.append(item.info())
        return {
            "page": page,
            "pageSize": pageSize,
            "total": total,
            "data": data
        }
    
    def getDataDictSetClass(self, datadictsetcode, page=1, pageSize =10, sortkey = "", query = "", ):
        if not datadictsetcode:
            return []
        datadictset = DataDictSet.objects(code = datadictsetcode).first()
        if not datadictset:
            return []
        if sortkey and sortkey[0] in "-+":
            sortkey = sortkey[0]
        else:
            sortkey = "+"
        sortkey = True if sortkey == "+" else False        
        result = set()
        for item in datadictset.datadict:
            tmp =item.fetch().codeclass
            if query and query not in tmp:
                continue
            result.add(tmp)
        result = list(result)
        result.sort(reverse=sortkey)
        total = len(result)
        if (page-1)*pageSize>len(result):
            result = []
        elif page*pageSize >len(result):
            result = result[(page-1)*pageSize:]
        else:
            reulst = result[(page-1)*pageSize: page*pageSize]
        return {
            "page": page,
            "pageSize": pageSize,
            "total": total,
            "data": result
        }

    def getDataDict(self, datadictsetcode, page = 1, pageSize = 10, sortkey = "", query= "",codeclass = ""):
        if not self.cache.get(datadictsetcode):
            data = DataDictSet.objects(code = datadictsetcode).first()

            if not data:
                return {
                    "page": page,
                    "pageSize": pageSize,
                    "total": 0,
                    "data": []
                }
            self.cache[datadictsetcode] = [item.fetch().info() for item in data.datadict]
        if sortkey and sortkey[0] not in "-+":
            sortkey = "+"+sortkey
        elif not sortkey:
            sortkey = "+name"
        if codeclass:
            data = [item for item in self.cache[datadictsetcode] if item["codeclass"] == codeclass] 
        else:
            data = self.cache[datadictsetcode]
        order, sort = sortkey[0], sortkey[1:] 
        data.sort(key=lambda x: x[sort])

        if order == "-": data = data[::-1]

        result = []
        index = 0  
        for item in data:
            if query in item["name"] or query in item["code"] or query in item["describe"] in query in item["describe"]:
                if (page-1)*pageSize<= index < page*pageSize:
                    result.append(item)
                index+=1
        return {
                    "page": page,
                    "pageSize": pageSize,
                    "total": index,
                    "data": result
                }

    def updateDataDictSet(self, datadictsetcode, name = "", describe = ""):
        if not datadictsetcode:
            return 1
        data = DataDictSet.objects(code = datadictsetcode).first()
        if not data:
            return 1
        data.name = name if name else data.name
        data.describe = describe if describe else data.describe
        try:
            data.save()
            self.cache = {}
            return 0
        except Exception as e:
            print(e)
            return 2
    
    def updateDataDict(self, codeid, name= "", code = "", describe = "", codeclass = ""):
        if not codeid:
            return 1
        data = DataDict.objects(codeid = codeid).first()
        if not data:
            return 1
        data.name = name if name else data.name
        data.describe = describe if describe else data.describe
        data.codeclass = codeclass if codeclass else data.codeclass
        data.code = code if code else data.code
        try:
            data.save()
            self.cache = {}
            return 0
        except Exception as e:
            print(e)
            return 2

    def deleteDataDictSet(self, datadictsetcode):
        if not datadictsetcode or not isinstance(datadictsetcode, list):
            return 1
        try:
            for item in datadictsetcode:
                deleteitem = DataDictSet.objects(code=item).first()
                print(deleteitem)
                if deleteitem:
                    for datadictitem in deleteitem.datadict:
                        datadictitem.fetch().delete()
                    deleteitem.delete()
                
        except Exception as e:
            print(e)
            return False
        self.cache = {}
        return True

    def deleteDataDict(self, datadictsetcode, datadictcode):
        if not datadictcode or not datadictsetcode or not isinstance(datadictcode, list): return 1
        datadictset = DataDictSet.objects(code = datadictsetcode).first()
        try:
            for item in datadictcode:
                deleteitem = DataDict.objects(codeid = item).first()
                if deleteitem and deleteitem in datadictset.datadict:
                    datadictset.datadict.remove(deleteitem)
                    deleteitem.delete()
            datadictset.save()
        except Exception as e:
            print(e)
            return  False
        self.cache = {}
        return True