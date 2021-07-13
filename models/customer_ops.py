from mongoengine import *
from datetime import datetime
from uuid import uuid4
from models.User import User
from libs.Singleton import Singleton
from models.Company import Company

class CustomerOps(DynamicDocument):
    coid = StringField(required=True)
    customer = StringField(required=True)
    account = StringField()
    # 技术人员
    technicalPerson = ListField(StringField())
    # 复核人员
    reviewer = ListField(StringField())
    # 上级
    monitorer = ListField(StringField())
    
    createdate = DateTimeField(default=datetime.now())
    def info(self):
        customer = User.objects(userid = self.customer).first()
        technical = []
        for item in self.technicalPerson:
            item = User.objects(userid = item).first()
            technical.append({
                "userid": item.userid,
                "username": item.username,
                "name": item.name
            })
        reviewers = []
        for item in self.reviewer:
            item = User.objects(userid = item).first()
            reviewers.append({
                "userid": item.userid,
                "username": item.username,
                "name": item.name
            })
        monitorers = []
        for item in self.monitorer:
            item = User.objects(userid = item).first()
            monitorers.append({
                "userid": item.userid,
                "username": item.username,
                "name": item.name
            })
        return {
            "coid": self.coid,
            "customer": {
                "userid": customer.userid,
                "username": customer.username,
                "name": customer.name
            }, 
            "technicalPerson": technical,
            "reviewer": reviewers,
            "monitorer": monitorers,
            "createdate": self.createdate.strftime("%Y-%m-%d %H:%M:%S"),
        }

@Singleton
class CustomerOpsControl:
    def gets(self, page=1, pagesize=10, sortkey=None, customer =None):
        if customer:
            cuops = CustomerOps.objects(cusotmer = customer)
        else:
            cuops = CustomerOps.objects()
        total = cuops.count()
        cuops  = cuops.order_by(sortkey if sortkey else "createdate")
        cuops = cuops.skip((page-1)*pagesize).limit(pagesize)
        result = [item.info() for item in cuops]
        return {
            "page": page,
            "pageSize": pagesize,
            "total": total,
            "data": result
        }
        
    def create_update(self, customer,  technicalPerson, reviewer, monitorer, account = '', coid = None): 
        if not isinstance(customer, dict) or not customer.get("userid"):
            return 20003, "客户信息格式不正确"
        customer = customer.get("userid")
        if not User.objects(userid=customer).first():
            return 20003, "客户不存在"
        if account and not Company.objects(managerid = customer, companyid = account).first():
            return 20003, "客户云账户不存在"
        if not coid:
            if not technicalPerson or not reviewer or not monitorer:
                return 20003, "技术|复核|监管人员不存在"
        if (technicalPerson and not isinstance(technicalPerson, list))\
                or (reviewer and not isinstance(reviewer, list))\
                or (monitorer and not isinstance(monitorer, list)):
            return 20003, "技术|复核|监管人员格式不正确"
        if not technicalPerson: technicalPerson = []
        if not reviewer: reviewer = []
        if not monitorer: monitorer = []
        for item in range(len(technicalPerson)):
            if not isinstance(technicalPerson[item], dict) or \
                not technicalPerson[item].get("userid") or \
                    not User.objects(userid=technicalPerson[item]["userid"]).first():
                return 20004, "技术人员{}无效".format(item)
            technicalPerson[item] = technicalPerson[item]["userid"]
        technicalPerson = list(set(technicalPerson))

        for item in range(len(reviewer)):
            if not isinstance(reviewer[item], dict) or \
                not reviewer[item].get("userid") or \
                    not User.objects(userid=reviewer[item]["userid"]).first():
                return 20004, "复核人员{}无效".format(item)
            reviewer[item] = reviewer[item]["userid"]
        reviewer = list(set(reviewer))

        for item in range(len(monitorer)):
            if not isinstance(monitorer[item], dict) or \
                not monitorer[item].get("userid") or \
                    not User.objects(userid=monitorer[item]["userid"]).first():
                return 20004, "监管人员{}无效".format(item)
            monitorer[item] = monitorer[item]["userid"]
        monitorer = list(set(monitorer))

        if not coid:
            cup = CustomerOps(coid = uuid4().hex, customer = customer, account = account, 
                    technicalPerson = technicalPerson, reviewer = reviewer, monitorer = monitorer)
            try:
                cup.save()
            except Exception as e:
                print(e)
                return 50003, "数据库异常"
            return 20000, "创建成功"

        cuos = CustomerOps.objects(coid = coid).first()
        if not cuos: return 40004, "更新id不存在"
        if customer:
            cuos.customer = customer
        if technicalPerson:
            cuos.technicalPerson = technicalPerson
        if account:
            cuos.account = account
        if reviewer: cuos.reviewer = reviewer
        if monitorer: cuos.monitorer = monitorer
        try:
            cuos.save()
            return 20000, "更新完成"
        except:
            return 50003, "数据库异常"
        
    
    def delete(self, customeropslist):
        if not customeropslist or not isinstance(customeropslist, list):
            return 40004, "提供错误参数集"
        result = []
        for item in set(customeropslist):
            result.append({
                    "id": item,
                    "success": False,
                    "reason": ""
                })
            cuops = CustomerOps.objects(coid = item).first()
            if not cuops:
                result[-1]["reason"] = "无效id值"
            else:
                try:
                    cuops.delete()
                    result[-1]["success"]= True
                except Exception as e:
                    result[-1]["reason"] = "删除失败:"+str(e)
        return 20000, result
