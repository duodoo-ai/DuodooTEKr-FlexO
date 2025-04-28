# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    multi_platform_app_max_file_upload_size = fields.Integer(
        string="The size of the multi-platform app upload file(MB)",
        config_parameter="multi_platform.app_max_file_upload_size",
        default=300,
    )
