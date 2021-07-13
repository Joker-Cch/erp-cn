from boto3 import client
import logging

class CloudFormation:
    def __init__(self):
        self.client = client("cloudformation")

    def start(self, option, args):
        if option == "create":
            if self.create(args.get("name"), args.get("url"), args.get("params")):
                logging.error("創建堆棧成功")
                return True
            else:
                logging.error("創建堆棧失敗")
        else:
            if self.delete(args.get("name")):
                logging.error("刪除堆棧成功")
                return True
            else:
                logging.error("刪除堆棧失敗")
                return False

    def create(self, name, url, params):
        for _ in range(3):
            try:
                resp = self.client.create_stack(
                    StackName = name,
                    TemplateURL = url,
                    Parameters = params
                )
                if resp.get("StackId"):
                    return True
            except Exception as e:
                logging.error(str(e))
        return False

    def delete(self, name):
        for _ in range(3):
            try:
                self.client.delete_stack(
                    StackName = name
                )
                return True
            except Exception as e:
                logging.error(str(e))
        return False