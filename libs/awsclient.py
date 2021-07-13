from boto3 import client
from botocore.exceptions import ClientError
from flask.logging import logging
from base64 import b64encode
from uuid import uuid4
def awsclient(service, ak=None, sk=None, region=None):
    try:
        awsserver = client(service, aws_access_key_id = ak, aws_secret_access_key = sk, region_name = region)
    except Exception as e:
        logging.error(str(e))
        return None
    return awsserver

def awsTempToken(ak, sk, region):
    aclient = awsclient("sts", ak, sk, region)
    try:
        data = aclient.get_session_token(DurationSeconds=900)
        if data.get("ResponseMetadata", {}).get("HTTPStatusCode", 0) == 200:
            secretinfo = b64encode((data["Credentials"]["AccessKeyId"]+"#1@2#3"+data["Credentials"]["SessionToken"]+"1Q@w#e"+data["Credentials"]["SecretAccessKey"]).encode('utf8')).decode("utf8")
            data = b64encode((secretinfo[:16]+uuid4().hex+secretinfo[16:]).encode('utf8')).decode('utf8')
            return data
        else:
            return None
    except Exception as e:
        logging.error(e)
        return None