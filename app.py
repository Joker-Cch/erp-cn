import os 
from flask import Flask, jsonify
from flask_mongoengine import MongoEngine
from config import getConfig, getEncryptKey
from views.UserManager import UserManager
from views.auth import Auth, auth
from views.UserInfo import UserInfo
from views.CompanyManage import CompanyManange
from views.awsservice import Awsservice
from views.ResourceGroupManage import RGManage 
from views.DataDictSet import DataDictSetManger
from views.MessagManager import MessageManager
from views.BosiCaseManager import CaseManage
from views.lambdatask import labmdaTask
from views.monitorService import monitorServiceView
from views.customerOps import CustomerOpsView
from libs.encrypt import Encrypt
from views.Report import makeImage


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    #加载配置文件
    app.config.from_object(getConfig())

    #配置mongodb
    db = MongoEngine(app)

    

    #配置redis
    
    #配置加解密密匙
    key = getEncryptKey()
    en = Encrypt()
    en.config(key, ase=True)
    @app.errorhandler(404)
    def not_found(error):
        return {
            "status": 40000,
            "msg": "接口不存在",
            "data": ""
        }, 404

    @app.errorhandler(500)
    def not_found(error):
        return {
            "status": 50000,
            "msg": "系统不存在",
            "data": ""
        }, 500
        


    #蓝图注册
    app.register_blueprint(UserManager, url_prefix = "/api/usermanager")
    app.register_blueprint(Auth, url_prefix = "/api")
    app.register_blueprint(UserInfo, url_prefix = "/api/userinfo")
    app.register_blueprint(CompanyManange, url_prefix = "/api/cloudaccount")
    app.register_blueprint(Awsservice, url_prefix = "/api/awsservice")
    app.register_blueprint(RGManage, url_prefix = "/api/resourcegroup")
    app.register_blueprint(DataDictSetManger, url_prefix = "/api/datadictset")
    app.register_blueprint(MessageManager, url_prefix = "/api/message")
    app.register_blueprint(CaseManage, url_prefix = "/api/casemanage")
    app.register_blueprint(labmdaTask, url_prefix = "/api/lambdatask")
    app.register_blueprint(monitorServiceView, url_prefix = "/api/monitorservice")
    app.register_blueprint(makeImage, url_prefix="/api/report")
    app.register_blueprint(CustomerOpsView, url_prefix = "/api/customerops")

    @app.route("/api")
    def index():
        return {
            "token": "set 'Authorization:Bosi <Token>' on Header",
            "request": "json body",
            "response": {
                "status": "状态码",
                "data": "响应数据",
                "msg": "响应信息"
                },
            "responsecode":{
                "20000": "请求并处理完成",
                "20002": "无效参数",
                "20003": "无效用户",
                "20004": "操作失败",
                "20005": "无效凭证",
                "20006": "服务不可寻",
                "20007": "无效ID",
                "20008": "无效数据类型",
                "40000": "请求路径不存在",
                "40001": "无权限访问",
                "50001": "系统异常"
            }
        }
    return app
