# -*- coding: utf-8 -*-
"""
@Time    : 2024/09/20 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
import os, requests, json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    def extract_name_path(self, data, result=None):
        if result is None:
            result = []

        if isinstance(data, list):
            for item in data:
                self.extract_name_path(item, result)
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
                self.extract_name_path(data['children'], result)
        return result

    def get_parent_path(self, path):
        # 分割路径为层级列表（注意转义反斜杠）
        parts = path.split('\\')
        # 剔除最后一个层级
        if len(parts) > 1:
            parent_parts = parts[:-1]
        else:
            return False  # 已经是根路径，直接返回
        # 重新拼接为完整路径
        parent_path = '\\'.join(parent_parts)
        return parent_path

    # 通过接口采集PhoenixAPI设备目录树数据
    def action_equipment_from_phoenix(self):
        # ===========================目录树===============================
        equipment_obj = self.env['maintenance.equipment']
        category_obj = self.env['maintenance.equipment.category']
        base_url = self.env['phoenix.token'].search([('name', '=', '获取PhoenixAPI网关接口调用token')])
        url_hierarchy = '{}'.format(base_url.url + ':' + base_url.port + '/v1/hierarchy?includePoints=true')

        string = "{} {}".format(base_url['token_type'], base_url['access_token'])

        # Step2：Setting Headers
        headers = {
            'Accept': 'application/json',
            'Authorization': '{}'.format(string)
        }

        # Step3：拼接访问权限
        data = ("grant_type={}&username={}&password={}"
                .format(base_url.grant_type, base_url.username, base_url.password))

        try:
            # 发送POST请求
            response = requests.get(url_hierarchy, headers=headers, data=data)
            response = json.loads(response.text)
            # _logger.info('目录树 -- {} -- '.format(response))
        except Exception as e:
            _logger.error('PhoenixAPI网关Token已超时{}，重新请求'.format(e))
            return
        # 使用示例（假设数据存储在变量json_data中）
        all_nodes = self.extract_name_path(response[0]['children'])
        for node in all_nodes:
            """处理分类数据"""
            category_id = category_obj.search([('name', '=', node['type'])])
            pv = {
                'name': node['type'],
            }
            if category_id:
                category_id.write(pv)
            else:
                category_obj.create(pv)
        for node in all_nodes:
            """新增或更新资产设备数据"""
            # _logger.info(f"{node['id']} | {node['name']} | {node['path'].replace("Company\\", "")} | {node['type']}")
            category_id = category_obj.search([('name', '=', node['type'])])
            equipment_id = equipment_obj.search([('asset_serial', '=', '{}'.format(node['id']))])
            path = r"{}".format(node['path'].replace("Company\\", ""))
            parent_path = self.get_parent_path(path)    # 分割路径为层级列表（注意转义反斜杠）
            parent_id = equipment_obj.search([('complete_path', '=', '{}'.format(parent_path))])
            uv = {
                'name': node['name'],
                'complete_path': node['path'].replace("Company\\", ""),
                'asset_serial': node['id'],
                'status': node['status'],
                'active': node['active'],
                'parent_id': parent_id.id,
                'category_id': category_id.id,
            }
            if equipment_id:
                equipment_id.write(uv)
            else:
                equipment_obj.create(uv)

