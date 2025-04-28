# -*- coding: utf-8 -*-
"""
@Time    : 2024/09/20 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
import os, requests, json
import logging, datetime
from datetime import datetime
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class PhoenixDynamicMeasurements(models.Model):
    _inherit = 'phoenix.dynamic.measurements'

    def check_monitor_data(self):
        """去查阈值报警功能的阈值设定,每个测点可以设置2个报警级别。计算数据结果写入到异常清单池中。"""
        alarm_obj = self.env['phoenix.alarm.pool']
        equipment_obj = self.env['maintenance.equipment']
        monitor_obj = self.env['phoenix.dynamic.measurements']
        monitor_records = monitor_obj.search([('alarm_origin', '!=', '温度'), ('async_state', '=', 0)])    # 源动态数据，告警记录。
        if len(monitor_records):
            for dynamic_id in monitor_records:
                serial_id = equipment_obj.search([('asset_serial', '=', dynamic_id.PointID)])  # 查询设备/测点内容
                pv = {
                    'measurement_point_id': serial_id.id or False,
                    'complete_path': serial_id.complete_path or False,
                    'category_id': dynamic_id.category_id if dynamic_id else '',
                    'name': dynamic_id.name if dynamic_id else '',
                    'monitor_time': dynamic_id.monitor_date if dynamic_id else None,
                    'async_time': fields.datetime.now(),
                }
                # 检查是否为 None
                if dynamic_id.high_alarm and dynamic_id.lower_warning:
                    # 告警动作逻辑，从最高告警信息反向查找(报警 > 警告)
                    if dynamic_id.high_alarm < dynamic_id.total:
                        pv.update({'monitor_value': dynamic_id.total if dynamic_id else 0})
                        alarm_obj.create(pv)
                    if dynamic_id.lower_warning < dynamic_id.total:
                        pv.update({'monitor_value': dynamic_id.total if dynamic_id else 0})
                        alarm_obj.create(pv)
            monitor_records.write({'async_state': 1})


    def check_temperature_monitor_data(self):
        """去查阈值报警功能的阈值设定,每个测点可以设置2个报警级别。计算数据结果写入到异常清单池中。"""
        alarm_obj = self.env['phoenix.alarm.pool']
        equipment_obj = self.env['maintenance.equipment']
        configurator_obj = self.env['phoenix.configurator']
        monitor_obj = self.env['phoenix.dynamic.measurements']
        monitor_records = monitor_obj.search([('alarm_origin', '=', '温度'), ('async_state', '=', 0)])
        # 将拿到的多个ID值转为唯一值
        unique_ids = list(set(monitor_records))
        # print(unique_ids)
        if len(unique_ids):
            for dynamic_id in unique_ids[0]:
                # 拿这个唯一值去查最近10条数据并从低到高排序
                configurator_interval = configurator_obj.search([('name', '=', '间隔样本数')])
                configurator_coefficient = configurator_obj.search([('name', '=', '温升系数')])
                monitor_record = monitor_obj.search([('PointID', '=', dynamic_id.PointID)],
                                             limit=f"{configurator_interval.value}",
                                             order='total asc')
                # print(monitor_record)
                # print(monitor_record[-1].total)
                if len(monitor_record) <= 1:
                    continue
                # 取用户自定义列表 (最后一个值 - 第一个值) / 温升系数
                if not configurator_interval.value:
                    monitor_value = (monitor_record[-1].total - monitor_record[0].total) / int(configurator_interval.value)
                    serial_id = equipment_obj.search([('asset_serial', '=', dynamic_id.PointID)])  # 查询设备/测点内容
                    pv = {
                        'measurement_point_id': serial_id.id or False,
                        'complete_path': serial_id.complete_path or False,
                        'category_id': dynamic_id.category_id if dynamic_id else '',
                        'name': dynamic_id.name if dynamic_id else '',
                        'monitor_time': dynamic_id.monitor_date if dynamic_id else None,
                        'async_time': fields.datetime.now(),
                    }
                    # # 检查是否为 None
                    if monitor_value and configurator_coefficient.value:
                        # 告警动作逻辑，从最高告警信息反向查找(报警 > 警告)
                        if monitor_value > configurator_coefficient.value:
                            pv.update({'monitor_value': monitor_value if monitor_value else 0})
                            alarm_obj.create(pv)
            monitor_records.write({'async_state': 1})

