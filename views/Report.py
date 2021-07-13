from flask import Blueprint, request, current_app
from libs.awsservice import *
from libs.awsclient import awsTempToken
from libs.awss3service import *
from libs.awssupport import awssupport
from libs.defResponse import success, nonauthorization
from models.Company import CompanyControl
from models.AwsTokenRecord import AwsRecordControl
from views.auth import auth
from datetime import datetime
from uuid import uuid4
import mimetypes
import os

makeImage = Blueprint("makeImage", __name__)

import boto3

@makeImage.route("/make_image", methods = ["POST"])
@auth.login_required
def image():
    if not request.json or not request.json.get("CompanyId") or not request.json.get("service_list") or not request.json.get("StartTime") or not request.json.get("EndTime") or not request.json.get("Unit") or not request.json.get("Region"):
        return success(20002, msg="缺少必要参数")
    service_list = request.json.get("service_list")

    aksk = CompanyControl().getAwsSecret(request.json.get("CompanyId"))
    if not aksk:
        return success(20007, msg="客户id不正确")

    dict_result = {}
    startTime = datetime.strptime(request.json.get("StartTime"), '%Y, %m, %d')
    endTime = datetime.strptime(request.json.get("EndTime"), '%Y, %m, %d')
    dict_result['Unit'] = request.json.get("Unit")
    P = []
    MetricName = ''
    for i in service_list:
        if not i.get("Namespace") or not i.get("Dimensions") or not i.get("ServiceType") or not i.get("Statistics") or not i.get("MetricName"):
            return success(20003, msg="缺少必要参数")
        service_dict = {}
        service_dict['serviceType'] = i.get("ServiceType")
        MetricName = i.get("MetricName")
        dict_result['type'] = MetricName
        # s3_client = boto3.client('s3', aws_access_key_id=aksk[0],
        #                          aws_secret_access_key=aksk[1],
        #                          region_name=request.json.get("Region"))
        # s3_client.download_file('bositool.file', '1.PNG', 'test.png')
        client = boto3.client('cloudwatch', aws_access_key_id=aksk[0],
                              aws_secret_access_key=aksk[1],
                              region_name=request.json.get("Region"))

        response = client.get_metric_statistics(
            Namespace=i.get("Namespace"),
            MetricName=i.get("MetricName"),
            Dimensions=i.get("Dimensions"),
            StartTime=startTime,
            EndTime=endTime,
            Period=int((endTime - startTime).total_seconds()),
            # Period=i.json.get("Period"),
            Statistics=i.get("Statistics"),
            Unit=request.json.get("Unit")
            # Unit='Percent'
        )
        p = {}
        j = response['Datapoints'][0]
        a = 1
        for en in i.get("Statistics"):
            k = j[en]
            p['k'+str(a)] = en
            p['v'+str(a)] = k
            a += 1
        service_dict['p'] = p
        P.append(service_dict)
    dict_result['P'] = P

    '''
     {
        'type':'cpu',
        'Unit':'Percent',
        'P': [
            {
                'serviceType':'ec2',
                'p': {
                    'k1': 'max',
                    'k2': 'avg',
                    'v1': '95',
                    'v2': '90'
                }
            }, {
                'serviceType':'rds',
                'p': {
                    'k1': 'max',
                    'k2': 'avg',
                    'v1': '94',
                    'v2': '91'
                }
            }, {
                'serviceType':'redis',
                'p': {
                    'k1': 'max',
                    'k2': 'avg',
                    'v1': '93',
                    'v2': '90'
                }
            }
        ]
     }
    '''
    print(111)
    print(dict_result)
    print(111)
    file_path = make_image(dict_result)

    s3_client = boto3.client('s3', aws_access_key_id=aksk[0],
                              aws_secret_access_key=aksk[1],
                              region_name=request.json.get("Region"))
    CompanyName = CompanyControl().getCompanyName(request.json.get("CompanyId"))
    dir = CompanyName + '/' + request.json.get("Region") + '/' + request.json.get("StartTime") + '-' + request.json.get("EndTime") + '/' + MetricName
    s3_client.upload_file(str(file_path), 'bositool.file', dir + '/test.png')
    return success(20000, msg="更新成功")


@makeImage.route("/list_image", methods=["POST"])
@auth.login_required
def list_image():
    if not request.json or not request.json.get("CompanyId") or not request.json.get("Region"):
        return success(20002, msg="缺少必要参数")
    aksk = CompanyControl().getAwsSecret(request.json.get("CompanyId"))
    if not aksk:
        return success(20007, msg="客户id不正确")
    s3_client = boto3.client('s3', aws_access_key_id=aksk[0],
                              aws_secret_access_key=aksk[1])
    CompanyName = CompanyControl().getCompanyName(request.json.get("CompanyId"))
    response = s3_client.list_objects(
        Bucket='bositool.file',
        Marker=CompanyName
    )
    k = []
    for i in response['Contents']:
        d = {}
        key = i['Key']
        if not key.startswith(CompanyName):
            continue
        # k.append(key)
        d['key'] = key
        d['url'] = 'https://s3.{}.amazonaws.com.cn/{}/{}'.format(request.json.get("Region"), 'bositool.file', key)
        k.append(d)
    return {
        "image": k
    }


from unittest import mock
from os.path import *


def get_chrome_driver():
    from selenium import webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


from snapshot_selenium import snapshot as driver
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.render import make_snapshot


def make_image(data):
    print("make in")
    metric = data["type"]
    unit = data['Unit']
    name_list = []
    for i in data["P"]:
        name_list.append(i["serviceType"])

    png = png_bar_chart(metric, unit, name_list, data)
    with mock.patch('snapshot_selenium.snapshot.get_chrome_driver', get_chrome_driver):
        make_snapshot(driver, png.render(), "{}.png".format(metric), 2, 2, True)
    file_path = os.path.abspath("/app") + "/{}.png".format(metric)
    print(file_path)
    return file_path


def png_bar_chart(metric, unit, x_name, data):
    bar = Bar(init_opts=opts.InitOpts(theme="white", bg_color="#c4ccd3"))
    bar.add_xaxis(x_name)

    k_list = []
    v_list = []
    for j in range(int((len(data['P'][0]['p'].keys()) / 2))):
        key = 'k' + str(j + 1)
        k_list.append(key)
        val = 'v' + str(j + 1)
        v_list.append(val)

    V = []
    a = 0
    for _ in range(len(v_list)):
        v = []
        for k in data['P']:
            v.append(k['p'][v_list[a]])
        V.append(v)
        a += 1
    print(V)

    a = 0
    for i in k_list:
        bar.add_yaxis(data['P'][0]['p'][i], V[a])
        a += 1

    bar.reversal_axis()
    bar.set_series_opts(label_opts=opts.LabelOpts(position="right"))
    bar.set_global_opts(title_opts=opts.TitleOpts(title="{}".format(metric),
                                                  pos_right="40%",
                                                  pos_top="15"),
                        legend_opts=opts.LegendOpts(pos_top="20",
                                                    pos_right="20",
                                                    orient="vertical"),
                        xaxis_opts=opts.AxisOpts(name="{}".format(unit)),
                        yaxis_opts=opts.AxisOpts(name="服务类型"))
    return bar