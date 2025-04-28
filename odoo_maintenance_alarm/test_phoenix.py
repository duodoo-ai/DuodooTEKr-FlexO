# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/17 11:20
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company:  目录树
"""
import requests
import json
import logging, datetime
_logger = logging.getLogger(__name__)

def extract_name_path(data, result=None):
    if result is None:
        result = []

    if isinstance(data, list):
        for item in data:
            extract_name_path(item, result)
    elif isinstance(data, dict):
        # 提取当前节点的name和path
        if 'name' in data and 'path' in data:
            result.append({
                'id': data['id'],
                'name': data['name'],
                'path': data['path'],
                'type': data.get('typeName', 'Unknown'),
                'status': data.get('status', []),
                'active': data.get('active', [])
            })
        # 递归处理子节点
        if 'children' in data and data['children'] is not None:
            extract_name_path(data['children'], result)
    return result

# ===========================Token===============================
# Step1：配置host地址、端口号、appKey和appSecret
# api config
grant_type = 'password'
username = 'admin'
password = 'admin'
url = 'http://192.168.1.100:14050'
url_token = url + '/token'

# Setting Headers
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = 'grant_type=password&username=admin&password=admin'

# 发送POST请求
response = requests.post(url_token, headers=headers, data=data)

# 打印响应内容
token = json.loads(response.text)

# ===========================目录树===============================
url_hierarchy = url + '/v1/hierarchy?includePoints=true'

string = "{} {}".format(token['token_type'], token['access_token'])

headers = {
    'Accept': 'application/json',
    'Authorization': '{}'.format(string)
}

data = 'grant_type=password&username=admin&password=admin'

# 发送POST请求
response = requests.get(url_hierarchy, headers=headers, data=data)
response = json.loads(response.text)
all_nodes = extract_name_path(response[0]['children'])

# """新增或更新资产设备数据"""
# print(f"{node['id']} | {node['name']} | {node['path'].replace("Company\\", "")} | {node['type']}")

# ===========================诊断数据===============================
# for node in all_nodes:
#     url_diagnoses = 'http://192.168.43.16:14050/v1/points/{}/diagnosesMeasurements'.format(2778)
#
#     string = "{} {}".format(token['token_type'], token['access_token'])
#
#     headers = {
#         'Accept': 'application/json',
#         'Authorization': '{}'.format(string)
#     }
#
#     data = 'grant_type=password&username=admin&password=admin'
#
#     # 发送POST请求
#     response = requests.get(url_diagnoses, headers=headers, data=data)
#
#     # 打印响应内容
#     diagnoses = json.loads(response.text)
#     print("诊断数据: {}".format(diagnoses))

# ===========================趋势数据===============================
# for node in all_nodes:
#     url_trend = 'http://192.168.43.16:14050/v1/points/{}/trendMeasurements'.format(2778)
#
#     string = "{} {}".format(token['token_type'], token['access_token'])
#
#     headers = {
#         'Accept': 'application/json',
#         'Authorization': '{}'.format(string)
#     }
#
#     data = 'grant_type=password&username=admin&password=admin'
#
#     try:
#         # 发送POST请求
#         response = requests.get(url_trend, headers=headers, data=data)
#         if response.status_code == 200:
#             # 打印响应内容
#             trend = json.loads(response.text)
#             print("趋势数据: {}".format(trend))
#         if response.status_code == 204:
#             print("趋势数据: {} ".format('The request was successfully completed but no content found.'))
#     except Exception as e:
#         print("趋势数据: {}".format(e))

# ===========================动态数据===============================
# for node in all_nodes:
#     url_dynamic = 'http://192.168.43.16:14050/v1/points/{}/dynamicMeasurements'.format(2778)
#
#     string = "{} {}".format(token['token_type'], token['access_token'])
#
#     headers = {
#         'Accept': 'application/json',
#         'Authorization': '{}'.format(string)
#     }
#
#     data = 'grant_type=password&username=admin&password=admin'
#
#     try:
#         # 发送POST请求
#         response = requests.get(url_dynamic, headers=headers, data=data)
#         if response.status_code == 200:
#             # 打印响应内容
#             dynamic = json.loads(response.text)
#             print("动态数据: {}".format(dynamic))
#         if response.status_code == 204:
#             print("动态数据: {} ".format('The request was successfully completed but no content found.'))
#     except Exception as e:
#         print("动态数据: {}".format(e))


from datetime import datetime
def search_monitor_date(data):
    """去查需要读取的数据"""
    for item in data:
        machine_id = item["MachineID"]
        point_id = item["ID"]
        name = item["Name"]
        # 检查 LastMeasurement 是否存在
        if item["LastMeasurement"]:
            monitor_date = item["LastMeasurement"]["ReadingTimeUTC"]
            units = item["LastMeasurement"]["Measurements"][0]["Units"]
            level = item["LastMeasurement"]["Measurements"][0]["Level"]
        else:
            monitor_date = None
            units = None
            level = None
        print(f"设备ID: {machine_id}, 测点ID: {point_id}, 测点名: {name}, 监测时间: {monitor_date}, 单位: {units}, 测值: {level}")


# date_from = "2025-01-14T08:30:04.74"
# date_to = "2025-01-14T08:30:08.74"
# fromDateUTC = datetime.strptime(date_from, '%Y-%m-%dT%H:%M:%S.%f')  # 当前时间倒推三十分钟
# toDateUTC = datetime.strptime(date_to, '%Y-%m-%dT%H:%M:%S.%f')  # 当前时间
# print(fromDateUTC)
# print(toDateUTC)
url_dynamic = '{}/v1/machines/{}/points'.format(url, 2761)

string = "{} {}".format(token['token_type'], token['access_token'])

headers = {
    'Accept': 'application/json',
    'Authorization': '{}'.format(string)
}

data = 'grant_type=password&username=admin&password=admin'
# 发送POST请求
response = requests.get(url_dynamic, headers=headers, data=data)
print(f"response: {response}")
try:
    if response.status_code == 200:  # 先检查响应状态码
        data = json.loads(response.text)  # 只有状态码为200时才解析JSON
        # print(f"动态数据: {data}")
        search_monitor_date(data)
    if response.status_code == 204:
        print("动态数据: {} ".format('The request was successfully completed but no content found.'))
except json.JSONDecodeError as e:
    # 捕获JSON解析错误（如返回内容非JSON格式）
    _logger.error(f"JSON解析失败: {e}, 响应内容：{response.text}")
except Exception as e:
    # 其他未知异常
    _logger.error(f'动态数据采集报错：{e}')



