# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/05 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class EquipmentMonitoringData(models.Model):
    _name = 'equipment.monitoring.data'
    _description = '位置指标数据'
    _inherit = ['mail.thread']
    _order = 'timestamp desc'
    _sql_constraints = [
        ('gps_coordinate_check',
         "CHECK(gps_longitude BETWEEN -180 AND 180 AND gps_latitude BETWEEN -90 AND 90)",
         "GPS坐标值非法"),
        ('battery_level_check',
         "CHECK(battery_level BETWEEN 0 AND 100)",
         "电池电量应在0-100%之间")
    ]

    # 基础字段
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='设备',
        required=True,
        ondelete='cascade'
    )
    timestamp = fields.Datetime(
        '上传时间',
        default=fields.Datetime.now,
        required=True
    )
    firmware_version = fields.Char(
        '固件版本',
        size=32,
        help="设备固件版本号，格式：VX.Y.Z"
    )

    # 系统状态
    memory_free = fields.Float(
        '剩余内存(MB)',
        digits=(8, 2),
        help="设备可用内存容量"
    )
    signal_strength = fields.Integer(
        '信号强度(dBm)',
        help="取值范围：-113（弱）到 -51（强）"
    )
    battery_level = fields.Float(
        '电池电量(%)',
        digits=(5, 2),
        help="剩余电池百分比"
    )

    # 环境传感器
    temperature = fields.Float(
        '温度(℃)',
        digits=(5, 2)
    )
    humidity = fields.Float(
        '湿度(%RH)',
        digits=(5, 2)
    )
    pressure = fields.Float(
        '压力(kPa)',
        digits=(8, 2),
        tracking=True
    )

    # 流体监测
    flow_rate = fields.Float(
        '流量(m³/h)',
        digits=(10, 2),
        tracking=True
    )
    liquid_level = fields.Float(
        '液位(m)',
        digits=(8, 3),
        tracking=True
    )

    # 位置信息
    gps_longitude = fields.Float(
        'GPS经度',
        digits=(9, 6),
        help="十进制格式，范围：-180.0 ~ 180.0"
    )
    gps_latitude = fields.Float(
        'GPS纬度',
        digits=(9, 6),
        help="十进制格式，范围：-90.0 ~ 90.0"
    )
    gsm_longitude = fields.Float(
        'GSM经度',
        digits=(9, 6)
    )
    gsm_latitude = fields.Float(
        'GSM纬度',
        digits=(9, 6)
    )

    # 气象数据
    wind_speed = fields.Float(
        '风速(m/s)',
        digits=(5, 2)
    )
    wind_direction = fields.Selection([
        ('N', '北'),
        ('NE', '东北'),
        ('E', '东'),
        ('SE', '东南'),
        ('S', '南'),
        ('SW', '西南'),
        ('W', '西'),
        ('NW', '西北')],
        string='风向'
    )

    # 热力图数据
    heatmap_data = fields.Binary(
        '信号热力图',
        help="热力图PNG图像数据"
    )
    heatmap_scale = fields.Float(
        '信号强度比例',
        digits=(3, 2),
        help="0.0~1.0表示信号覆盖强度"
    )

    @api.constrains('signal_strength')
    def _check_signal_strength(self):
        for record in self:
            if not (-113 <= record.signal_strength <= -51):
                raise ValidationError(_("信号强度应在-113到-51 dBm之间"))

    def action_generate_heatmap(self):
        """生成热力图方法（需具体实现）"""
        self.ensure_one()
        # 示例伪代码
        # heatmap = generate_heatmap(self.gps_longitude, self.gps_latitude, self.signal_strength)
        # self.write({
        #     'heatmap_data': base64.b64encode(heatmap.getvalue()),
        #     'heatmap_scale': self._calculate_heat_scale()
        # })
        return True

    def _calculate_heat_scale(self):
        """计算热力值比例"""
        # 示例算法
        return (self.signal_strength + 113) / 62  # 将-113~-51映射到0~1

    