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


class MaintenanceAlertRule(models.Model):
    _inherit = 'maintenance.alert.rule'

    parameter_name = fields.Selection(
        selection=[
            ('rotational_speed', '设备转速'),
            ('vibration_speed', '振动速度'),
            ('acceleration_envelope_2', '二段加速度包络'),
            ('acceleration_envelope_3', '三段加速度包络'),
            ('temperature', '设备温度')
        ],
        string='监控参数',
        required=True
    )

    # 动态单位显示
    def _get_parameter_unit(self):
        units = {
            'rotational_speed': self.spec_id.speed_unit,
            'vibration_speed': 'mm/s',
            'acceleration_envelope_2': 'g',
            'acceleration_envelope_3': 'g',
            'temperature': self.spec_id.temp_unit
        }
        return units.get(self.parameter_name, '-')

    # 增强阈值检查
    def _check_thresholds(self):
        super()._check_thresholds()
        for rule in self:
            if rule.parameter_name == 'temperature' and rule.spec_id.temp_unit == 'f':
                if rule.min_value < -459.67:
                    raise ValidationError(_("华氏温度不能低于-459.67℉"))

