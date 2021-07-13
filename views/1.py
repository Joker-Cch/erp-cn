import boto3
from datetime import datetime, timedelta



client = boto3.client('cloudwatch', aws_access_key_id='AKIAUKTTXEQSLNSAH223',
                      aws_secret_access_key='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',
                      region_name='cn-northwest-1')
endTime = datetime(2020, 10, 24)
startTime = datetime(2020, 10, 23)
response = client.get_metric_statistics(
    Namespace='CWAgent',
    MetricName='mem_used_percent',
    Dimensions=[
        {
            "Name": "InstanceId",
            "Value": "i-06f6f7c1f61bf681f"
        },
        {
            "Name": "ImageId",
            "Value": "ami-0e7b2f9353a132016"
        },
        {
            "Name": "InstanceType",
            "Value": "t2.micro"
        }
    ],
    StartTime=datetime(2020, 10, 23),
    EndTime=datetime(2020, 10, 24),
    Period=int((endTime - startTime).total_seconds()),
    Statistics=[
        'Maximum', 'Average'
    ],
    # Unit='Percent'
    # Unit='None'
)

# response = client.get_metric_data(
#     MetricDataQueries=[
#         {
#             'Id': 'string',
#             'MetricStat': {
#                 'Metric': {
#                     'Namespace': 'AWS/RDS',
#                     'MetricName': 'NetworkTransmitThroughput',
#                     'Dimensions': [
#                         {
#                             'Name': 'DBInstanceIdentifier',
#                             'Value': 'smsdb'
#                         }
#                     ]
#                 },
#                 'Period': int((datetime(2020, 10, 12) - datetime(2020, 10, 11)).total_seconds()),
#                 'Stat': 'Sum',
#                 # 'Unit': 'Percent'
#             },
#             # 'Expression': 'string',
#             # 'Label': 'string',
#             'ReturnData': True
#             # 'Period': int((datetime(2020, 10, 12) - datetime(2020, 10, 11)).total_seconds())
#         },
#     ],
#     StartTime=datetime(2020, 10, 11),
#     EndTime=datetime(2020, 10, 12),
#     # NextToken='string',
#     # ScanBy='TimestampDescending'|'TimestampAscending',
#     # MaxDatapoints=123
# )

print(response)
for i in response['Datapoints']:
    print(i['Average'])

# s3_client = boto3.client('s3', aws_access_key_id='AKIAUKTTXEQSLNSAH223',
#                       aws_secret_access_key='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',
#                       region_name='cn-northwest-1')
# # s3_client.upload_file('./pyvenv.cfg', 'bositool.file', 'aaa/vv1v/tes2t.png')
#
# marker = 'aaa'
# response = s3_client.list_objects(
#     Bucket='bositool.file',
#     Marker=marker
# )
#
# for i in response['Contents']:
#     key = i['Key']
#     if not key.startswith(marker):
#         continue
#     print(key)