# -*- coding: utf-8 -*-

import ast
import json
from odoo import models, _
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        ICP = self.env["ir.config_parameter"].sudo()
        current_user = self.env.user
        current_user_company = current_user.company_id

        session_info = super(Http, self).session_info()
        project = {
            "pipeline": {
                "normal_state_color": ICP.get_param(
                    "water_supply_pipeline.normal_state_color", default="#a3cfbb"
                ),
                "exception_state_color": ICP.get_param(
                    "water_supply_pipeline.exception_state_color", default="#fff3cd"
                ),
            },
            "large_screen": {
                "title": ICP.get_param(
                    "water_supply_pipeline.large_screen_title",
                    default=_("Smart water supply operation system"),
                ),
                "background_color": ICP.get_param(
                    "water_supply_pipeline.large_screen_background_color", default="#004b7a"
                ),
            },
        }

        session_info.update({"project": project})
        return session_info
