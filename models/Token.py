"""
用户凭证管理

"""
from hashlib import sha256
from uuid import uuid4
from time import time
import redis
import json
import os
from libs.Singleton import Singleton

# ==凭证管理==  
@Singleton
class Token():
    # ===初始化Redis连接===  
    def __init__(self, RedisConfig = None):
        # 读取系统变量，创建连接
        self.db = redis.StrictRedis(host = os.getenv("REDIS_HOST","localhost"), port=int(os.getenv("REDIS_PORT", 6379)), db=0)

    # === 保存凭证 ===
    def SaveToken(self, token, user):
        self.db.set(token, user, ex=86400)
        return True if self.db.get(token) else False

    # === 生成凭证 ===
    def genToken(self, userid, userrole):
        # userid： 用户id
        # userrole: 用户角色
        starttime = time()
        token = sha256()
        user = "#..#".join([str(starttime),userid])
        token.update(user.encode('utf8') )
        token = token.hexdigest()
        user = json.dumps({
            "starttime": starttime, 
            "userid": userid,
            "role": userrole
        })
        if self.SaveToken(token,user):
            return {"token": token}
        else:
            return None
    
    # === 获取凭证 ===
    def getToken(self, token):
        # token： 用户凭证
        user = self.db.get(token)
        if not user: return False
        data = json.loads(user)
        return {"userid": data["userid"],"token": token, "role":data["role"]}
    
    # === 删除凭证 ====
    def delToken(self, token):
        #token: 用户凭证
        self.db.delete(token)

    def getLambdaToken(self, token):
        return True if self.db.get("LambdaToken#"+token) else False

    def setLambdaToken(self, token):
        return self.SaveToken("LambdaToken#"+token, uuid4().hex)