# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Company(models.Model):
    _inherit = 'res.company'

    fax = fields.Char(related='partner_id.fax', store=True, readonly=False)