# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _


class View(models.Model):
    _inherit = 'ir.ui.view'

    def _render_template(self, template, values=None):
        # 只在登录页面和后端页面执行
        if template in ['web.login', 'web.webclient_bootstrap']:
            if not values:
                values = {}
            ICP = self.env["ir.config_parameter"].sudo()
            system_name = ICP.get_param("eist_erp.system_name", default="EIST ERP")
            values["title"] = system_name
        return super(View, self)._render_template(template, values)
