# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/05 16:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class MaintenanceEquipmentSpec(models.Model):
    _inherit = 'maintenance.equipment.spec'

    # 新增监控指标字段
    parameter_type = fields.Selection(selection_add=[
        ('rotation', '旋转参数'),
        ('vibration', '振动参数'),
        ('temperature', '温度参数')
    ], ondelete={'rotation': 'cascade', 'vibration': 'cascade', 'temperature': 'cascade'})

    # 旋转参数
    rotational_speed = fields.Float(
        '转速(RPM)',
        digits=(8, 2),
        help="当前设备旋转速度"
    )
    speed_unit = fields.Selection(
        [('rpm', 'RPM'),
         ('rad_s', 'rad/s')],
        string='转速单位',
        default='rpm'
    )

    # 振动参数
    vibration_speed = fields.Float(
        '振动速度(mm/s)',
        digits=(6, 3)
    )
    acceleration_envelope_2 = fields.Float(
        '二段加速度包络(g)',
        digits=(6, 4)
    )
    acceleration_envelope_3 = fields.Float(
        '三段加速度包络(g)',
        digits=(6, 4)
    )

    # 温度参数
    temperature = fields.Float(
        '设备温度(℃)',
        digits=(5, 1)
    )
    temp_unit = fields.Selection(
        [('c', '℃'),
         ('f', '℉')],
        string='温度单位',
        default='c'
    )

    @api.constrains('temperature')
    def _check_temp_range(self):
        if self.temp_unit == 'c' and self.temperature < -273.15:
            raise ValidationError(_("摄氏温度不能低于绝对零度(-273.15℃)"))

    # 单位转换方法
    def convert_speed_to_rpm(self):
        for record in self:
            if record.speed_unit == 'rad_s':
                return record.rotational_speed * 9.5492968  # rad/s转RPM
            return record.rotational_speed

    def convert_temp_to_celsius(self):
        for record in self:
            if record.temp_unit == 'f':
                return (record.temperature - 32) * 5 / 9
            return record.temperature

    # 增强校验规则
    @api.constrains(
        'rotational_speed',
        'vibration_speed',
        'acceleration_envelope_2',
        'acceleration_envelope_3',
        'temperature'
    )
    def _check_monitor_values(self):
        for record in self:
            error_msgs = []
            if record.rotational_speed < 0:
                error_msgs.append(_("转速不能为负值"))
            if record.vibration_speed < 0:
                error_msgs.append(_("振动速度不能为负值"))
            if record.temperature < -273.15 and record.temp_unit == 'c':
                error_msgs.append(_("温度不能低于绝对零度"))
            if error_msgs:
                raise ValidationError("\n".join(error_msgs))

    health_score = fields.Float(
        '健康指数',
        # compute='_compute_health_score',
        store=True,
        digits=(3, 2)
    )

    # def _compute_health_score(self):
    #     for record in self:
    #         score = 100.0
    #         # 根据阈值计算扣分逻辑
    #         for alert in record.alert_rule_ids:
    #             if alert.is_triggered:
    #                 score -= alert.severity_level * 10
    #         record.health_score = max(score, 0)
