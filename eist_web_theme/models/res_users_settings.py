# -*- coding: utf-8 -*-


from odoo import fields, models


class ResUsersSettings(models.Model):
    _inherit = "res.users.settings"

    drawermenu_config = fields.Json(string="Drawer Menu Configuration", readonly=True)
