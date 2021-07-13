"""
资源组管理  
* 资源定义  
    * groupid: 组id  
    * company: 客户id  
    * createauthorid： 创建者id  
    * groupname： 组名  
    * envname： 环境名  
    * region： 区域  
    * serviceType： 服务类型  
    * resource： 资源  
    * createdate： 创建时间  

资源组数据管理
"""
from mongoengine import *
from datetime import datetime
from uuid import uuid4
from models.Company import Company
from models.User import User
from libs.Singleton import Singleton

# ==资源组定义==  
class ResourceGroup(DynamicDocument):
    groupid = StringField(required= True, unique=True)
    companyid = StringField(required= True)
    createauthorid = StringField(required=True)
    groupname = StringField(required= True)
    envname = StringField(required=True)
    region = StringField(required= True)
    serviceType = StringField(required=True)
    resource  = ListField(StringField(), required=True)
    createdate = DateTimeField(default = datetime.now())

    # === 资源组详情 ===
    def info(self):
        return {
            "groupid": self.groupid,
            "companyid": self.companyid,
            "createauthorid": self.createauthorid,
            "groupname": self.groupname,
            "envname": self.envname,
            "region": self.region,
            "serviceType": self.serviceType,
            "resource": self.resource,
            "createdate": self.createdate.strftime("%Y-%m-%d %H:%M:%S")
        }

    # === 资源简略信息 ===
    def sampleinfo(self):
        return {
            "groupid": self.groupid,
            "companyid": self.companyid,
            "createauthorid": self.createauthorid,
            "groupname": self.groupname,
            "envname": self.envname,
            "region": self.region,
            "serviceType": self.serviceType,
            "createdate": self.createdate.strftime("%Y-%m-%d %H:%M:%S")
        }

# ==资源组数据层==  
@Singleton
class ResourceGroupControl:

    # === 初始化===  
    def __init__(self):
        # 初始化用户映射和客户映射
        self.usermap =  {}
        self.companymap = {}

    # ===获取资源组详情===
    def getRG(self, groupid):
        # groupid: 资源组id
        rg = ResourceGroup.objects(groupid= groupid).first()
        if rg:
            info = rg.info()
            info["companyname"] = Company.objects(companyid = info["companyid"]).first().companyname
        else:
            info = None
        return info 
    
    # === 资源组列表 ===
    def getRGlist(self, page = 1, pagesize = 10, sortkey=None, query = "", 
        companyid = None, region = None, envname = None, serviceType = None):
        #page: 页码  
        #pagesize: 行数   
        #sortkey: "+|-"+key: 排序key  
        #query： 查询条件，模糊查询组名环境名      
        # compamyid: 客户id 查询相关客户的资源组
        # region: 区域id
        # envname： 环境名
        # serviceType： 服务类型
        if query: query = Q(groupname__icontains=query)|Q(envname__icontains=query)
        if companyid: query=(query&Q(companyid__in = companyid)) if query else Q(companyid__in = companyid)
        if envname: query = (query&Q(envname = envname)) if query else Q(envname = envname)
        if region: query = (query&Q(region=region)) if query else Q(region = region)
        if serviceType: query = (query&Q(serviceType=serviceType)) if query else Q(serviceType=serviceType)
        rg = ResourceGroup.objects(query) if query else ResourceGroup.objects()
        
        total = rg.count()
        rg = rg.order_by(sortkey if sortkey else "createdate").skip((page-1)*pagesize).limit(pagesize)

        result = []
        for item in rg.order_by("createdate"):
            # 查询创建者名称
            if self.usermap.get(item.createauthorid):
                username = self.usermap[item.createauthorid]
            else:
                username = User.objects(userid = item.createauthorid).first().username 
                self.usermap[item.createauthorid] = username
            #查询客户名
            if self.companymap.get(item.companyid):
                companyname = self.companymap.get(item.companyid)
            else:
                companyname = Company.objects(companyid = item.companyid).first().companyname
                self.companymap[item.companyid] = companyname
            tmp = item.sampleinfo()
            tmp["username"]  = username
            tmp["companyname"] = companyname
            result.append(tmp)
        return {
            "page": page,
            "pageSize": pagesize,
            "total": total,
            "data": result
        }
    
    # ===添加资源组===
    def addRG(self,companyid,createauthorid,groupname,envname,region,serviceType,resource):
        # companyid 客户id
        # createauthorid： 创建者id
        # groupname: 组名
        # envname： 环境名称
        # region： 区域
        # serviceType： 服务类型
        # resource： 资源列表
        data = ResourceGroup(groupid=uuid4().hex,companyid=companyid,createauthorid=createauthorid, \
            groupname=groupname,envname= envname,region= region,serviceType = serviceType,resource=resource)
        try:
            data.save()
            return True
        except Exception as e:
            print(e)
            return False
    
    # ===更新资源组===
    def updateRG(self, groupid, groupname = '', envname = '', resource= ''):
        # groupid： 资源组id
        # groupname: 资源组名
        # envname： 环境名
        # resource： 资源列表

        updatedata = {}
        if groupname: updatedata["groupname"] = groupname
        if envname: updatedata["envname"]  = envname
        if resource: updatedata["resource"] = resource
        if not updatedata: return 1
        try:
            rg = ResourceGroup.objects(groupid = groupid).first()
            if not rg:
                return 2
            rg.update(**updatedata)
            return 0
        except Exception as e:
            print(e)
            return 3
    # ===删除资源组===
    def deleteRG(self, group):
        #资源组列表3
        try:
            for item in group:
                print(item)
                ResourceGroup.objects(groupid = item).delete()
            return True
        except Exception as e:
            print(e)
            return False