# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/05 16:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields, api


class MaintenanceInspection(models.Model):
    _name = 'maintenance.inspection'
    _description = '设备巡检记录'
    _order = 'inspection_date desc'

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='设备',
        required=True
    )
    inspection_date = fields.Datetime(
        '检查时间',
        default=fields.Datetime.now
    )
    inspector_id = fields.Many2one(
        'res.users',
        string='检查人员',
        default=lambda self: self.env.user
    )
    status = fields.Selection([
        ('normal', '正常'),
        ('warning', '警告'),
        ('fault', '故障')],
        string='设备状态',
        required=True
    )
    remarks = fields.Text('检查备注')
    image = fields.Binary('现场照片')
    checklist_line_ids = fields.One2many(
        'inspection.checklist.line',
        'inspection_id',
        string='检查项'
    )


class InspectionChecklistLine(models.Model):
    _name = 'inspection.checklist.line'
    _description = '检查项明细'

    inspection_id = fields.Many2one(
        'maintenance.inspection',
        string='巡检记录'
    )
    name = fields.Char('检查项', required=True)
    standard = fields.Char('检查标准')
    result = fields.Selection([
        ('pass', '合格'),
        ('fail', '不合格')],
        string='检查结果'
    )
    note = fields.Text('备注')