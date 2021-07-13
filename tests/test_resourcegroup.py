from pprint import pprint

class TestRg:

    def test_add(self, client, header, args):

        data = client.post("/api/resourcegroup/add", headers = header, json = args["args"]["rgadd"])
        assert data.status_code == 200
        data = data.get_json()
        print(data)
        assert data["status"] == 20000

    def test_rgs(self, client, header, args):
        url = "/api/resourcegroup/groups?"+"&".join([key+"="+str(value) for key, value in args["args"]["rglist"].items()])
        data = client.get(url, 
            headers = header
        )

        assert data.status_code == 200
        data = data.get_json()
        assert data["status"] == 20000
        data = client.get(url.split("?")[0]+"?companyid=3cefbed4a2dc4a34a86a28b9dfaf7928", 
            headers = header
        ).get_json()
        print(",".join([item["groupid"] for item in data["data"]]))
        assert len(data["data"]) == 0

    def test_update(self, client, header, args):
        url = "/api/resourcegroup/update"
        data = client.post(url, headers = header, json = args["args"]["rgupdate"])
        assert data.status_code == 200
        data = data.get_json()
        assert data["status"] == 20000

    def test_groupinfo(self, client, header, args):
        url = "/api/resourcegroup/groupinfo?groupid=" + args["args"]["rgupdate"]["groupid"]
        data = client.get(url, headers = header)
        assert data.status_code == 200
        assert data.get_json()["status"] = 20000
    
    def test_delete(self, client, header, args):
        url = "/api/resourcegroup/delete"
        data = client.post(url, headers= header, json = args["args"]['rgdelete'])
        assert data.status_code == 200
        assert data.get_json()["status"]  == 20000