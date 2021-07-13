from flask import Blueprint, request, current_app
from functools import wraps
from models.Token import Token
from libs.defResponse import success, nonauthorization
from models.BosiCase import BosiCaseControl
from libs.awssupport import LambdaTaskTrigger

tokenmanager = Token()

labmdaTask = Blueprint("LambdaTask", __name__)


def lambdaauth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization", "Bosi ").split(" ")[-1]
        if not tokenmanager.getLambdaToken(token):
            return nonauthorization()
        else:
            return f(*args, **kwargs)
    return decorated_function

@labmdaTask.route("/tasks", methods = ["GET"])
@lambdaauth
def tasks():
    tasknums, data = BosiCaseControl().getCaseTask()
    if tasknums == 0:
        LambdaTaskTrigger(current_app.config.get("LAMBDATASK_AK", None),
            current_app.config.get("LAMBDATASK_SK", None)).disabled(
                current_app.config.get("LAMBDATASK_EVENTNAME", 'BosiCaseCrontab'),
                current_app.config.get("LAMBDATASK_EVENTBUS", 'default'))
    return success(20000, data = data)

@labmdaTask.route("/callback", methods = ["POST"])
@lambdaauth
def callback():
    """
    {'202008130c9ad0a818': 
        {'status': True, 
         'data': {'awscaseid': 'case-917958955567-muen-2020-dce4f8b9363650f4', 
                 'awscasedisplayid': '7298462801', 'awscasestatus': 'unassigned'}
        }
    }
    """
    if not request.json: return success(20000, "任務爲空")
    status, waittasknums = BosiCaseControl().updateByCallBack(request.json)
    if waittasknums == 0:
        LambdaTaskTrigger(current_app.config.get("LAMBDATASK_AK", None),
            current_app.config.get("LAMBDATASK_SK", None)).disabled(
                current_app.config.get("LAMBDATASK_EVENTNAME", 'BosiCaseCrontab'),
                current_app.config.get("LAMBDATASK_EVENTBUS", 'default'))
    return success(20000, data = "task callback")

# @labmdaTask.route("/trigger")
# @lambdaauth
# def trigger():
#     lambdaName = current_app.config.get("LAMBDA_NAME")
#     appurl = current_app.config.get("APP_URL")
    
