"""
**用户管理模块**  
1. 用户数据层  
2. 用户数据管理层  
"""
from mongoengine import *
from datetime import datetime
from uuid import uuid4
from hashlib import md5
from libs.Singleton import Singleton
"""
用户数据层  

  * **表定义**   
      * 用户表  
            |列名|  必填|  类型|  说明  |  
            userid Y string 用户id   
            username Y string 用户名    
            mail Y string 用户邮箱地址   
            password Y string 用户密码  
            status Y bool 用户状态, True:启用，False： 停用 
            role Y string 用户角色 目前有admin， user， company  
            name Y string 用户昵称   
            info Y string 用户简介  
            phone Y string 用户手机号码  
  * **方法定义**  
      * get_id: 输出用户  
      * userinfo： 输出用户信息  
"""
class User(DynamicDocument):
    # ===表定义===
    userid = StringField(required=True, unique= True) 
    username = StringField(required= True, unique= True)
    mail  = EmailField(required=True, unique= True)
    password = StringField(required=True)
    status = BooleanField(default= True)
    role = StringField(required=True, default='user')
    name = StringField(required= True)
    info = StringField()
    phone = StringField()
    createdate = DateTimeField(default = datetime.now())

    # === get_id ###
    def get_id(self):
        return self.userid

    # === userindo ##
    def userinfo(self):
        return {
            "userid": self.userid,
            "username": self.username,
            "mail": self.mail,
            "status": self.status,
            "name": self.name, 
            "info": self.info,
            "phone": self.phone,
            "role": self.role, #admin,users, company
            "createdate": self.createdate.strftime("%Y-%m-%d %H:%M:%S")
        }

"""
用户数据管理层  
    方法定义  
       * loginUser  用户身份验证入口  
       * checkpassword  密码检查  
       * updateUser  更新用户数据接口  
       * getUsers  获取用户列表  
       * getUserInfo  获取用户信息  
       * addUser  添加用户  
       * deleteUser 删除用户  
       * generateId  生成用户id  
       * generateId  生成密码   
"""
@Singleton
class UserControl:
    # === 初始化 ===  

    # 创建用于检验用户信息key  
    def __init__(self):
        self.userkey = ["username", "name", "mail", "info", "phone", "status"]
    
    # === 用户身份校验入口 ==
    def loginUser(self, username, password):
        """
        * username: 用户名或者用户邮箱  
        * password: 用户密码   
        """
        password = self.genpassword(password)
        user = User.objects(username = username, password = password, status = True).first()
        if not user:
            user = User.objects(mail = username, password = password, status = True).first()
        return user.userinfo() if user else None

    def getCompanylist(self):
        user = []
        for item in User.objects(role="company").all():
            user.append({
                "userid": item.userid,
                "username": item.username,
                "name": item.name
            })
        return {
            "users": user
        }


    # ===用户修改密码===
    def checkpassword(self, userid, oldpassword, newpassword, admin = False):
        """
        * userid: 用户id  
        * oldpassword: 旧密码，在admin=False有效  
        * newpassword: 新密码，在admin=True有效  
        * 判断修改者是不是admin  
        """
        if admin:
            try:
                User.objects(userid = userid).update_one(set__password = self.genpassword(newpassword))
                return 0
            except Exception as e:
                print(e)
                return 2
        #查询用户是否存在
        user = User.objects(userid = userid, password = self.genpassword(oldpassword)).first()
        if not user: return 1
        try:
            User.objects(userid = userid, password = self.genpassword(oldpassword)).update_one(set__password = self.genpassword(newpassword))
            return 0
        except Exception as e:
            print(e)
            return 2

    # === 更新用户信息
    def updateUser(self, userid, data):
        """
        userid: 用户id

        data:
        username：用户名  
        name：昵称  
        mail： 邮箱  
        info： 简介  
        phone: 手机号码  
        status: 用户状态 
        """
        setdata = {}
        for key, value in data.items():
            if key in self.userkey:
                setdata[key] = value
        if not setdata: return False
        try:
            User.objects(userid=userid).update(**setdata)
            return True
        except Exception as e:
            print(e)
            return False

    # === 获取用户列表 ===  
    def getUsers(self, page=1, pagesize=10, sortkey=None, query = '', role = None):
        #page: 页码  
        #pagesize: 行数   
        #sortkey: "+|-"+key: 排序key  
        #role: 查询用户
        #query： 查询条件，模糊查询用户名，昵称， 手机号码， 邮箱  
        users = None
        
        if query:
            query = Q(username__icontains=query)|Q(name__icontains = query)|\
                Q(phone__icontains=query)|Q(mail__icontains=query)
        if role:
            query  = Q(role=role) if not query else query&Q(role = role)
    
        users = User.objects(query) if query else User.objects()

        # 统计查询结果
        total = users.count() 

        #排序
        users = users.order_by(sortkey) if sortkey else users.order_by("createdate")
        #返回结果
        users = users.skip((page-1)*pagesize).limit(pagesize)

        result = []
        for item in users:
            result.append(item.userinfo())
        return {
            "page": page,
            "pageSize": pagesize,
            "total": total,
            "data": result
        }
    
    def getCaseAssginUser(self):
        return [item.userid for item in User.objects(role='user').all()]


    #===用户个人信息查询===  
    def getUserInfo(self, userid):
        #userid： 用户id
        user = User.objects(userid =userid).first()
        return user.userinfo() if user else  None

    
    # ===添加用户=== 
    def addUser(self, username, mail, password, phone, name,role, info=None):
        # username: 用户名  
        # mail： 邮箱  
        # password： 密码  
        # phone： 手机号码  
        # name: 昵称   
        # role： 用户权限： 默认user  
        # info： 用户简介  
        user = User(userid=self.generateId(), username = username, mail = mail,
        # 生成密码  
        password = self.genpassword(password), phone = phone, name = name, role = role,info = info)
        try:
            user.save()
            return True
        except Exception as e:
            print(e)
            return False

    # ===删除用户===  
    def deleteUser(self, userid):
        # userid: 用户id
        try:
            for item in userid:
                user = User.objects(userid = item).first()
                if user.username != "admin":
                    user.delete()
            return True
        except Exception as e:
            print(e)
            return False

    # ===生成用户id=== 
    def generateId(self):
        return uuid4().hex

    # ===生成密码===  
    def genpassword(self, password):
        # 哈希值加密  
        data = password
        md5gen = md5()
        md5gen.update(data.encode("utf8"))
        return md5gen.hexdigest()