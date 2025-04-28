# -*- coding: utf-8 -*-


from odoo import fields, models


class ResMultiPlatformDevices(models.Model):
    _name = "res.multi_platform.devices"
    _description = "Multi-platform client device management"

    name = fields.Char(string="Device Name")
    device_type = fields.Selection(
        [("computer", "Computer devices"), ("mobile", "Mobile devices")], string="Device Type"
    )
