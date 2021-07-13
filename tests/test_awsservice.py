from pprint import pprint
class TestAwsservice:
    def test_20000(self, client, header, args):
        data = client.post("/api/awsservice/search", 
            json = args["args"]["awsservice"], headers = header)
        assert data.status_code == 200
        data = data.get_json()
        assert data["status"] == 20000
        
        assert isinstance(data["data"], list)

    
    def test_20002(self, client, header, args):
        data = client.post("/api/awsservice/search", 
            json = {}, headers = header)
        assert data.status_code == 200
        data = data.get_json()
        assert data["status"] == 20002
        assert data["msg"] == "缺少必要参数"
    
    def test_20006(self, client, header, args):
        ag = args["args"]["awsservice"]
        ag["ServiceType"]  = "TESGWTEGRWETGQEWFDWTGEWTFDWGW#ETGGEWREWTRFEWREWFGERWT"
        data = client.post("/api/awsservice/search", 
            json = ag, headers = header)
        assert data.status_code == 200
        data = data.get_json()
        assert data["status"] == 20006
        assert data["msg"] == "服务不存在"

    def test_20007(self, client, header, args):
        ag = args["args"]["awsservice"]
        ag["CompanyId"]  = "TESGWTEGRWETGQEWFDWTGEWTFDWGW#ET"
        data = client.post("/api/awsservice/search", 
            json = args["args"]["awsservice"], headers = header)
        assert data.status_code == 200
        data = data.get_json()
        assert data["status"] == 20007
        assert data["msg"] == "客户id不正确"