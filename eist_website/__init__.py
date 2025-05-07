# -*- coding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID

def uninstall_hook(env):
    """
    卸载模块时，删除所有有关主题的设置
    """
    parameters = env["ir.config_parameter"].sudo().search([("key", "=like", "eist_website%")], limit=None)

    if parameters:
        for parameter in parameters:
            parameter.unlink()
