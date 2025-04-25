# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/17 11:20
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@mobile  : 18951631470
"""
from odoo import api, fields, models
from odoo.exceptions import UserError


class CleanBusinessData(models.Model):
    _name = 'clean.business.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '清理记录'

    @api.model
    def _get_business_table_name(self):
        return self._get_business_table_name_impl()

    @api.model
    def _get_business_table_name_impl(self):
        """默认取business.data.table 里的所有业务数据表清理"""
        return self.env['business.data.table'].search([])

    need_clean_table = fields.One2many('business.data.table', 'clean_business_id',
                                       default=_get_business_table_name,
                                       string='要清理的业务数据表')
    need_clean_log = fields.One2many('clean.business.log', 'clean_business_id', string='清理日志')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    def name_get(self):
        """在name字段里显示 id_清理记录"""
        self.ensure_one()
        res = []
        for record in self:
            res.append((record.id, '上次清理时间 / ' +
                        str(self.env['clean.business.log'].search([], limit=1).write_date.strftime("%Y-%m-%d %H:%M:%S"))))
        return res

    def remove_data(self):
        sql_list = []
        trunc_success = False
        try:
            for line in self.need_clean_table:
                obj_name = line.name
                obj = self.env[obj_name]
                if obj._table:
                    sql = "TRUNCATE TABLE %s CASCADE " % obj._table
                    self.env.cr.execute(sql)
                    sql_list.append(sql + ';')
                    trunc_success = True
            if trunc_success:
                self.need_clean_log.create({
                    'clean_business_id': self.id,
                    'sql': ''.join(sql_list)
                })
        except Exception as e:
            raise UserError(e)
        return


class BusinessDataTable(models.Model):
    _name = 'business.data.table'
    _description = '业务数据表'

    model = fields.Many2one('ir.model',
                            string='需要清理的表',
                            domain=['&', ('model', 'not like', 'res%'), ('model', 'not like', 'base%')]
                            )
    name = fields.Char(string='业务数据表名', required=True)
    clean_business_id = fields.Many2one('clean.business.data', string='清理数据对象')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.onchange('model')
    def onchange_model(self):
        self.name = self.model and self.model.model


class BusinessDataLog(models.Model):
    _name = 'clean.business.log'
    _description = '清理日志'
    _order = 'id desc'

    clean_business_id = fields.Many2one('clean.business.data', string='清理数据对象')
    sql = fields.Text(string='SQL')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)


