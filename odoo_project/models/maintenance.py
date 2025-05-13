# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/10 08:50
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

    location_id = fields.Many2one('project.map.location', index=True, string='Project Map Location')  # 泵站绑定  自动显示项目/名称
    serial_no = fields.Char(string="IMEI")  # 序列号 (IMEI)，设备唯一标识码

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """ 根据上下文中的 location_id 动态过滤设备 """
        location_id = self.env.context.get('search_default_location_id')
        if location_id:
            domain += [('location_id', '=', location_id)]
        # 调用父类方法，仅传递支持的参数
        return super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order
        )

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.serial_no})" if record.serial_no else record.name
            result.append((record.id, name))
        return result



