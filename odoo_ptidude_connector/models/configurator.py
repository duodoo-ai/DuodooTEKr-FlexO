# -*- coding: utf-8 -*-
"""
@Time    : 2024/09/20 08:50
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


class PhoenixConfigurator(models.Model):
    _name = 'phoenix.configurator'
    _description = '参数'

    name = fields.Char(string='参数', required=True)
    value = fields.Char(string='值', required=True)
    active = fields.Boolean(string='启用', default=True)
    note = fields.Char(string='备注')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # def unlink(self):
    #     for record in self:
    #         if record.note:
    #             raise UserError('不能删除系统创建的类别')