from botocore.exceptions import ClientError,EndpointConnectionError
import re
from libs.awsclient import awsclient as connect
    
def getInstanceId(ak, sk, region, cording = {}):
    ec2 = connect("ec2", ak, sk, region)
    filter_by = []
    newcording = {}
    for key, value in cording.items():
        if key and value:
            filter_by.append({
                "Name":"tag-key",
                "Values": [key]
            })
        
            newcording[key] = re.compile(".*"+value+".*")
    cording = newcording
    try:
        response  = ec2.describe_instances(Filters = filter_by, MaxResults =10000)
    except EndpointConnectionError as e:
        return 404
    except ClientError as e:
        return 401
        
    if not response or not response.get("Reservations") or not response.get("Reservations"):
        return []
    
    result = []
    for group in response.get("Reservations"):        
        for item in group.get("Instances"):
            tags = ",".join(["=".join(tag.values()) for tag in item.get("Tags", [])])
            if cording and not any([True for rule in cording.values() if tags and rule.match(tags)]): continue
            result.append({
                "InstanceId": item.get("InstanceId"),
                "InstanceType": item.get("InstanceType"),
                "LaunchTime": item.get("LaunchTime"),
                "State": item.get("State", {}).get("Name"),
                "Tags": tags,
                "ServiceType": "EC2",
                "VpcId": item.get("VpcId"),
                "SubnetId": item.get("SubnetId"),
                "Architecture": item.get("Architecture"),
                "Platform": item.get("Platform", 'Linux'),
                "AvailabilityZone": item.get("Placement", {}).get("AvailabilityZone"),
                "GroupName": item.get("Placement", {}).get("GroupName")
            })
    return result

def getRDS(ak, sk, region, cording):
    rds = connect("rds", ak, sk, region)
    
    rds.describe_db_instances()

def SearchAws(service, ak, sk, region, cording):
    searchFunction = {
        "EC2": getInstanceId,
    }
    func = searchFunction.get(service, None)
    return func(ak, sk, region, cording) if func else func