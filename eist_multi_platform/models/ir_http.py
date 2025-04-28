# -*- coding: utf-8 -*-

from odoo import models
import logging

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        IrConfigSudo = self.env["ir.config_parameter"].sudo()

        multi_platform_app_max_file_upload_size = int(
            IrConfigSudo.get_param(
                "multi_platform.app_max_file_upload_size",
                default=300,
            )
        )

        session_info = super(IrHttp, self).session_info()

        session_info.update(
            {"multi_platform_app_max_file_upload_size": multi_platform_app_max_file_upload_size}
        )

        return session_info
