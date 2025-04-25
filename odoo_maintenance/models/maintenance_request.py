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


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    # --------------------------------------------------------------
    # Corrective    纠正性维护：设备发生故障后的应急维修（被动响应）（如电机损坏、传感器失灵）。默认设为 corrective。
    # Preventive    预防性维护：按计划定期执行的维护任务（主动预防）（如每月润滑、季度校准）。
        # 类型：preventive
        # 子任务：关联 inspection（巡检）和 calibration（校准）。
        # 示例：每月执行一次电机巡检（inspection），每月执行一次设备润滑（inspection），每季度校准传感器（calibration）。
    # Inspection    巡检任务：日常状态检查（属于预防性维护的子类，但需要独立跟踪）
    # Calibration   校准任务：参数调整（可以是预防或纠正的一部分，但需单独管理）
        # 操作：修复突发故障（如更换损坏的继电器）。
    # Installation  安装调试：新设备部署或系统升级（完全独立于维护周期）
        # 独立流程：无需关联预防或纠正性维护，单独跟踪安装调试进度。
    # --------------------------------------------------------------
    maintenance_type = fields.Selection(
        selection_add=[
            ('inspection', 'Inspection'),     # 巡检任务
            ('calibration', 'Calibration'),    # 校准任务
            ('installation', 'Installation'),   # 安装调试
        ],
        ondelete={
            'inspection': 'set null',  # 删除类型时设为空，而非强制回退到 corrective
            'calibration': 'set null',
            'installation': 'set null'
            }
    )

