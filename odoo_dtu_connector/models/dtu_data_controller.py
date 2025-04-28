# -*- coding: utf-8 -*-
"""
@Time    : 2025/02/27 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import api, models

class DtuDataController(models.AbstractModel):
    _name = 'dtu.data.controller'
    _description = 'DTU Data Collection Controller'

    @api.model
    def start_dtu_service(self):
        dtu_service = self.env['dtu.data.service']
        dtu_service.start_service()