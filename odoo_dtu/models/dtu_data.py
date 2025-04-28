# -*- coding: utf-8 -*-
"""
@Time    : 2025/02/27 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields

class DtuData(models.Model):
    _name = 'dtu.data'
    _description = 'DTU Data Collection'

    name = fields.Char(string="Name", required=True, index="trigram")
    imei = fields.Char(string='IMEI')  # 序列号(IMEI)，设备唯一标识码
    time = fields.Datetime(string='Upload time')  # 上传时间
    model = fields.Char(string='Model')  # 型号
    version = fields.Char(string='Version')  # 版本
    running_time = fields.Char(string='Running time')  # 运行时间
    remaining_memory = fields.Char(string='Remaining memory')  # 剩余内存
    signal_strength = fields.Float(string='Signal strength', digits='Signal')  # 信号强度
    pressure = fields.Float(string='Pressure', digits='Pressure')  # 压力
    traffic = fields.Float(string='Traffic', digits='Traffic')  # 流量
    liquid_level = fields.Float(string='Liquid level', digits='Liquid')  # 液位
    temperature = fields.Float(string='Temperature', digits='Temperature')  # 温度
    atmospheric_pressure = fields.Float(string='Atmospheric pressure', digits='Atmospheric')  # 气压
    humidity = fields.Float(string='Humidity', digits='Humidity')  # 湿度
    gps_longitude = fields.Float(string='Gps Longitude', digits='Gps')  # GPS经度
    gps_latitude = fields.Float(string='Gps Latitude', digits='Gps')  # GPS纬度
    gsm_longitude = fields.Float(string="Gsm Longitude", digits='Gsm')  # GSM经度
    gsm_latitude = fields.Float(string="Gsm Latitude", digits='Gsm')  # GSM纬度
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        change_default=True,
        default=lambda self: self.env.company)