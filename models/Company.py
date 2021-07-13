"""
客户信息表  
    * comepanyid： 客户id  
    * comepanyname: 客户名称  
    * awsaccount: aws账户  
    * awsared: aws区域： global全球， cn中国  
    * awsaccesskey: aws ak  
    * awssecretkey： aws sk  
    * contactperson: 对接人  
    * contactphone: 对接人号码  
    * contactmail: 对接人邮箱  
    * companyinfo： 对接人信息  
    * createdate： 创建时间  
    * function：
        * info： 基本信息
        * awsserect: aksk 
客户信息管理  
"""
from mongoengine import *
from datetime import datetime
from uuid import uuid4
from libs.encrypt import Encrypt
from libs.Singleton import Singleton

class Company(DynamicDocument):
    companyid = StringField(require=True, unique=True)
    companyname = StringField(required=True, unique=True)
    managerid = StringField(required=True)
    awsaccount = StringField(require=True)
    awsarea = StringField(required=True)
    awsaccesskey = StringField(required=True)
    awssecretkey = StringField(required=True)
    contactperson = StringField(required=True)
    contactphone = StringField(required=True)
    contactmail = EmailField(required=True)
    companyinfo = StringField()
    createdate = DateTimeField(default=datetime.now())
    
    def info(self):
        en = Encrypt()
        ak, sk = en.decode(self.awsaccesskey), en.decode(self.awssecretkey)
        return {
            "companyid": self.companyid,
            "companyname": self.companyname,
            "managerid": self.managerid,
            "awsaccount": self.awsaccount,
            "awsarea": self.awsarea,
            "contactperson": self.contactperson,
            "contactmail": self.contactmail,
            "contactphone": self.contactphone,
            "companyinfo": self.companyinfo,
            "createdate": self.createdate.strftime("%Y-%m-%d %H:%M:%S"),
            "awsaccesskey": ak[:3]+ "*"*(len(ak)-6)+ak[-3:],
            "awssecretkey": sk[:3]+ "*"*(len(sk)-6)+sk[-3:]
        }
    
    def awssecret(self):
        en = Encrypt()
        return (en.decode(self.awsaccesskey), en.decode(self.awssecretkey))

@Singleton
class CompanyControl:
    def enctrypt(self, ak=None, sk=None):
        en = Encrypt()
        if ak:
            key = en.genSecret()
            ak = en.encode(key, ak)
        if sk:
            key = en.genSecret()
            sk = en.encode(key, sk)
        return ak, sk

    def getCompanys(self, page=1, pagesize=10, sortkey=None, query = '', managerid = None):
        companys = None
        query = Q(companyname__icontains = query)|\
                Q(companyinfo__icontains = query)|Q(contactmail__icontains=query)|\
                Q(contactphone__icontains=query)|Q(contactperson__icontains=query) \
                    if query else None
        if managerid:
            query =  query&Q(managerid = managerid) if query else Q(managerid = managerid)            
        companys = Company.objects(query)
        total = companys.count()
        companys = companys.order_by(sortkey) if sortkey else companys.order_by("createdate")
        companys = companys.skip((page-1)*pagesize).limit(pagesize)
        result = []
        for item in companys:
            result.append(item.info())
        return {
            "page": page,
            "pageSize": pagesize,
            "total": total,
            "data": result
        }

    def getCompanyName(self, companyid):
        result = Company.objects(companyid = companyid).first()
        return result.companyname if result else None

    def checkCompany(self, managerid, companyid):
        company = Company.objects(managerid = managerid, companyid=companyid).first()
        return True if company else False
        
    def getAwsSecret(self, companyid):
        company = Company.objects(companyid = companyid).first()
        return company.awssecret() if company else None

    def addCompany(self, managerid, companyname, awsaccount, awsaccesskey, awssecretkey, contactperson, \
        contactphone, contactmail,companyinfo = '' , awsarea ="global"):
        awsaccesskey, awssecretkey = self.enctrypt(awsaccesskey, awssecretkey)
        company = Company(managerid = managerid, companyid = uuid4().hex, companyname= companyname, \
            awsaccount= awsaccount, awsarea = awsarea, awsaccesskey = awsaccesskey, awssecretkey = awssecretkey, \
            contactperson = contactperson, contactphone=contactphone, contactmail = contactmail, companyinfo =companyinfo)
        try:
            company.save()
            return True
        except Exception as e:
            print(e)
            return False

    def deleteCompany(self, company):
        try:
            for item in company:
                Company.objects(companyid = item).first().delete()
            return True
        except Exception as e:
            print(e)
            return False
    
    def updateCompany(self, companyid, data):
        vaild_key = ["companyid", "companyname", "companyinfo", "awsaccount", "awsaccount", "awsarea", "awsaccesskey", "awssecretkey", "contactperson", "contactphone", "contactmail", "managerid"]
        try:
            for item in list(data.keys()):
                if item not in vaild_key or not data.get(item):
                    data.pop(item)
            if not data: return False
            company = Company.objects(companyid=companyid).first()
            if not company: return False
            if "*"*5 in data.get("awsaccesskey", "*"*5):
                data.pop("awsaccesskey")
            elif data.get("awsaccesskey"):
                data["awsaccesskey"], _ = self.enctrypt(data["awsaccesskey"])
            if "*"*5 in data.get("awssecretkey", "*"*5):
                data.pop("awssecretkey")
            elif data.get("awssecretkey"):
                data["awssecretkey"], _ = self.enctrypt(data["awssecretkey"])
            company.update(**data)
            return True
        except Exception as e:
            print(e)
            return False