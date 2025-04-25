# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/13 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
import os, io
import logging
import qrcode
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import http
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class EquipmentTechnicalCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    technical_type = fields.Selection(
        selection=[
            ('control', 'Control'), # 控制类
            ('motor', 'Motor'),   # 电机类
            ('sensor', 'Sensor'),  # 传感类
            ('relay', 'Relay'),   # 继电类
            ('electronic', 'Electronic'),  # 电子类
            ('protocol', 'Protocol'),    # 协议类
            ('serial', 'Serial'),      # 串口类
            ('other', 'Other'),  # 其他类
        ],
        string='Equipment Technical Category', default='other'
    )
    active = fields.Boolean(string='Active', default=True)

