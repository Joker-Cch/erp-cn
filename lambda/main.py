from executor.case.Case import Case
from executor.session import Session
from os import getenv
from logger import bslog as logging

def handler(event, context):
    url = getenv("APIURL", "http://localhost:5000/api/lambdatask")
    path = {
        "tasks": getenv("TASKPATH", "tasks"),
        "callback": getenv("TASKCALLBACK", "callback")
    }
    api_token = getenv("APITOKEN", 'test1234')
    
    if not url and api_token:
        logging.error("缺少必要参数")
        exit(0)
    session = Session()
    session.config(url, api_token)
    case = Case(path)
    case.start()
    logging.info("退出应用中")

def monitor(event, context):
    pass


if __name__ == "__main__":
    handler('', '')

"""
from executor.session import Session 
from executor.case.Case import Case
session = Session()
session.config("http://localhost:5000/api/lambdatask",  "test1234")
path = {'tasks': 'tasks', 'callback': 'callback'}
case = Case(path)
case.start()
https://s3-ap-southeast-1.amazonaws.com/cf-templates-883tzuli64hy-ap-southeast-1/20202364FP-lambdatask.yml

export APITOKEN=u06X5jPPolHeCXb6xJQX/Xm3oRKw3yIRzT0YwYjBo3s
export APIURL=http://161.189.69.74/api/lambdatask
export 
"""

