import os 
from random import randint
class Config:
    DEBUG = False
    TESTING = False
    MONGODB_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGODB_USERNAME = "bositool"
    MONGODB_PASSWORD = "bosicloud888"
    MONGODB_PORT = 27017
    MONGODB_DB = "bositool"
    MONGODB_CONNECT = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "5f352379324c22463451387a0aec5d2f")
    SESSION_COOKIE_NAME = "BosiTool"
    LAMBDATASK_AK = "AKIA5LOU6CIX4DLDSUXR"
    LAMBDATASK_SK = "BJ/YuSDeoPbq1ZY/nCACesrpXqA7htC7ObKQspdA"
    LAMBDATASK_EVENTNAME = "BosiCaseCrontab"

    AWSS3INFO = {
        "region": "cn-northwest-1",
        "ak": "AKIAUKTTXEQSKSU3DEPI", 
        "sk": "+FeiqjbVrickqeXcqCnK5Kim8X3Mf32cEfaEV8IM",
        "bucket": "bositool.file"
    }

class ProductionConfig(Config):
    ENVNAME= "product"

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True

def getConfig():
    execEnv = os.environ.get("APIENV", "product")
    execEnv = "dev"
    if execEnv == "product":
        return ProductionConfig()
    elif execEnv == "dev":
        return DevelopmentConfig()
    else: 
        return TestingConfig()

def getEncryptKey(keypath = "./encryptkey.txt"):
    key = os.environ.get('ENCRYPTKEY', None)
    if not key and os.path.exists(keypath):
        with open(keypath, encoding='utf8') as f:
            key = []
            for item in f.readlines():
                item = item.strip()+"".join([chr(randint(97,122)) for item in range(16)])
                key.append(item[:16])
    if not key:
        key = set()
        while len(key)<= 16:
            key.add("".join([chr(randint(97,122)) for item in range(16)]))
    return list(key) if isinstance(key, set) else key