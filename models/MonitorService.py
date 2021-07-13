from mongoengine import *
from datetime import datetime
from uuid import uuid4
from flask.logging import logging
from models.User import User
from models.Company import Company
from models.ResourceGroup import ResourceGroup


class monitorGroup(DynamicDocument):
    mgid = StringField(required=True, unique=True)
    mgname = StringField(required=True)
    msid = StringField(required=True)
    servicetype = StringField(required= True)
    rgid = ListField(StringField())
    metrics = ListField(StringField())
    def info(self):
        try:
            rgs = [item.sampleinfo() for item in ResourceGroup.objects(groupid__in = self.rgid).all()]
        except Exception as e:
            logging.error(str(e))

            return {}

        return {
            "mgid": self.mgid,
            "mgname": self.mgname,
            "msid": self.msid,
            "servicetype": self.servicetype, 
            "resourcegroups": rgs,
            "metrics": self.metrics
        }

class monitorService(DynamicDocument):
    msid = StringField(required=True, unique=True)
    msname = StringField(required=True)
    business = StringField(required=True)
    customer = StringField(required= True)
    cloudaccount = StringField(required= True)
    monitorperiod = StringField(required=True)
    monitorenv = StringField(requeired = True)
    monitorarea = StringField(required=True)
    reportpersonid  = StringField(required=True)
    monitorgroup = ListField(LazyReferenceField(monitorGroup))
    createtime = DateTimeField(required=True)

    def info(self):
        try:
            customer = User.objects(userid = self.customer).first()
            reportpersonname = User.objects(userid = self.reportpersonid).first()
            if not customer :
                customer = ''
            else:
                customer = "{}({})".format(customer.username, customer.name)
            if not reportpersonname:
                reportpersonname = ''
            else:
                
                reportpersonname = "{}({})".format(reportpersonname.username, reportpersonname.name)
            
        except Exception as e:
            logging.error(str(e))
            return {}
        try:
            cloudaccount = Company.objects(companyid = self.cloudaccount).first()
            if not cloudaccount: return {}
        except Exception as e:
            logging.error(str(e))
            return {}
        return {
            "msid": self.msid,
            "msname": self.msname, 
            "bussiness": self.business, 
            "customerid": self.customer,
            "customername": customer,
            "cloudaccountid": self.cloudaccount,
            "monitorenv": self.monitorenv,
            "monitorarea": self.monitorarea,
            "reportpersonid": self.reportpersonid,
            "reportpersonname": reportpersonname,
            "cloudaccountname": cloudaccount.companyname,
            "monitorperiod": self.monitorperiod,
            "monitorgrouptotal": len(self.monitorgroup)
        }

class MonitorServiceControl:
    def get_config(self, customer):
        if not customer:
            return 40004, "缺少客户id"
        
        if not User.objects(userid = customer, role="company").first():
            return 20003, "无效客户id"

        cloudaccount = Company.objects(managerid = customer).all()
        if not cloudaccount:
            return 20003, "客户未创建云账户"

        result = {item.companyid:{} for item in cloudaccount}
        for cloudaccountid in result.keys():
            for item in ResourceGroup.objects(companyid = cloudaccountid).all():
                if not result[cloudaccountid].get(item.region):
                    result[cloudaccountid][item.region] = {item.envname:[item.serviceType]}
                elif not result[cloudaccountid][item.region].get(item.envname):
                    result[cloudaccountid][item.region][item.envname] = [item.serviceType]
                elif item.serviceType not in areas[item.region][item.envname]:
                    result[cloudaccountid][item.region][item.envname].append(item.serviceType)
            result[cloudaccountid] = {
                "status": True if result[cloudaccountid] else False, 
                "data": result[cloudaccountid] if result[cloudaccountid] else "未创建资源组"
            }
            
        
        return 20000, result 
            

    def add(self, msname, customer, cloudaccount, business, monitorperiod,monitorenv, monitorarea, reportpersonid, groups):
        serviceid = uuid4().hex
        monitorservice = monitorService(
            msid = serviceid,
            msname = msname, 
            customer = customer,
            cloudaccount  = cloudaccount, 
            business = business, 
            monitorperiod = monitorperiod,
            createtime = datetime.now(),
            monitorenv = monitorenv,
            monitorarea = monitorarea,
            reportpersonid = reportpersonid
            )
        for item in range(len(groups)):
            groups[item] = monitorGroup(
                mgid = uuid4().hex,
                msid = serviceid,
                mgname = groups[item].get("mgname"),
                servicetype = groups[item].get("servicetype"),
                rgid = groups[item].get("resourcegroup"),
                metrics = groups[item].get('metrics')
            )
        index = 0 
        while index<len(groups):
            try:
                groups[index].save()
            except Exception as e:
                for item in range(index):
                    groups[item].delete()
                return False, "服务器异常"
            index += 1 
        
        monitorservice.monitorgroup = groups
        try:
            monitorservice.save()
            return True, ("添加成功", monitorservice.msid)
        except Exception as e:
            logging.error(str(e))
            for item in groups:
                item.delete()
            return False, "服务器异常"

    def delete(self, msids):
        result = []
        for item in msids:
            ms = monitorService.objects(msid = item).first()
            if not ms: result.append({"monitorserviceid": item, "success": False, "reason": "not found"})
            for msc in ms.monitorgroup:
                try:
                    msc.fetch().delete()
                except Exception as e:
                    logging.error(str(e))
            try:
                ms.delete()
                result.append({"monitorserviceid": item, "success": True, "reason": ""})
            except Exception as e:
                logging.error(str(e))
                result.append({"monitorserviceid": item, "success": False, "reason": str(e)})
        return result
            
                
    def update(self, msid, msname, customer, cloudaccount, business,
        monitorperiod, groups):
        ms = monitorService.objects(msid = msid).first()
        if not ms:
            return False, (40004, "服务不存在")
        if msname: ms.msname = msname
        if customer: ms.customer  = customer
        if cloudaccount: ms.cloudaccount = cloudaccount
        if monitorperiod: ms.monitorperiod = monitorperiod
        if business: ms.business = business
        mscids  = [item.fetch().mgid for item in ms.monitorgroup]
        for item in range(len(groups)):
            if groups[item].get("mgid"):
                msc = monitorGroup.objects(mgid = groups[item]["mgid"]).first()
                if groups[item].get("mgname"):
                    msc.mgname = groups[item]["mgname"]
                if groups[item].get("servicetype"):
                    msc.servicetype = groups[item].get("servicetype")
                if groups[item].get("resourcegroup"):
                    msc.rgid = groups[item].get("resourcegroup")
                if groups[item].get("metrics"):
                    msc.metrics = groups[item]["metrics"]
            else:
                msc = monitorGroup(
                    mgid = uuid4().hex,
                    msid = ms.msid,
                    mgname = groups[item].get("mgname"),
                    servicetype = groups[item].get("servicetype"),
                    rgid = groups[item].get("resourcegroup"),
                    metrics = groups[item].get('metrics')
                )
            try:
                msc.save()
            except Exception as e:
                for deleteitem in range(item):
                    try:
                        groups[deleteitem].delete()
                    except Exception as e:
                        logging.error(str(e))
                return False, (50000, str(e))
            if msc.mgid in mscids:
                mscids.pop(mscids.index(msc.mgid))

            groups[item] = msc
        if mscids:
            for item in monitorGroup.objects(mgid__in = mscids).all():
                try:
                    item.delete()
                except Exception as e:
                    logging.error(str(e))

        ms.monitorgroup = groups
        try:
            ms.save()
        except Exception as e:
            logging.error(str(e))
            return False, (50000, str(e))
        return True, (20000, "更新成功")


    def gets(self, page=1, pagesize=10, sortkey=None, customer =None, cloudaccount= None, business= ""):
        result = []
        try:
            query = None
            if customer: query = Q(customer = customer)
            if cloudaccount:  Q(cloudaccount = cloudaccount) if not query else  Q(cloudaccount = cloudaccount)&query
            if business: Q(business = business) if not query else Q(business = business)|query
            mss =  monitorService.objects() if not query else monitorService.objects(query)
            mss = mss.order_by(sortkey) if sortkey else mss.order_by("createtime")
            total = mss.count()
            result = [item.info() for item in mss.skip((page-1)*pagesize).limit(pagesize)]
            status = True
        except Exception as e:
            logging.error(str(e))
            status = False
            result = str(e)
            

        return {
            "page": page, 
            "pageSize": pagesize,
            "total": total if status else 0,
            "data": result
        }

    def getitem(self, msid):
        return [item.info() for item in monitorGroup.objects(msid = msid).all()]

    def checkaccess(self, msid, customer):
        return monitorService.objects(msid = msid, customer = customer).first() != None  