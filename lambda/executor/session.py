import requests 
from executor.Singleton import Singleton
from logger import bslog as logging

@Singleton
class Session:
    def config(self, url, token = None):
        self.url = url
        self.headers = {"Authorization": "Bosi {}".format(token)} if token else None

    def get(self, path, data, timeout=5, repeat= 1):
        error_info = set()
        for _ in range(repeat):
            try:
                resp = requests.get(self.url+"/" + path.strip("/"), params= data,  timeout = timeout, headers = self.headers)
            except Exception as e:
                logging.error(str(e))
                continue
            if resp.status_code == 200:
                resp = resp.json()
                if resp["status"]  == 20000:
                    return True, resp["data"] if resp["data"] else resp["msg"]
                else:
                    return False,  resp["msg"]
            else:
                error_info.add(resp.content.decode('utf8')+'\n')
        logging.error("\n\n".join(error_info))
        return False, "\n\n".join(error_info)
    
    def post(self, path, data, timeout = 5, repeat= 1):
        error_info = set()
        for _ in range(repeat):    
            try:
                resp = requests.post(self.url+"/" + path.strip("/"), json= data,  timeout = timeout, headers = self.headers)
            except Exception as e:
                logging.error(str(e))
                continue
            if resp.status_code == 200:
                resp = resp.json()
                if resp["status"]  == 20000:
                    return True, resp["data"] if resp["data"] else resp["msg"]
                else:
                    return False,  resp["msg"]
            else:
                error_info.add(resp.content+'\n')
                
        logging.error("\n\n".join(error_info))
        return False, "\n\n".join(error_info)
