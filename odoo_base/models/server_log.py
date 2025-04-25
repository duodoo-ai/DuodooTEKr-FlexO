# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/17 11:20
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@mobile  : 18951631470
"""
from odoo import fields, models


class ServerLog(models.Model):
    _name = 'server.log'
    _description = '收集接口日志'

    name = fields.Char(string='操作日志', help='同步日志')
    model_id = fields.Many2one('ir.model', string='模型',
                               ondelete="set null",
                               index=True, help='来源模型')

    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

