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
        theme = session_info["theme"]

        disable_theme_customizer = current_user_company.theme_id.disable_theme_customizer

        theme_id = current_user.theme_id
        if disable_theme_customizer:
            # 如果关闭用户定制主题功能，则使用公司绑定的主题
            theme_id = current_user_company.theme_id

        # 主题 3. Theme color
        # -------------------------------------------------------
        theme_color_list = [
            {"id": 0, "name": _("Light")},
            {"id": 1, "name": _("Dark blue")},  # 深蓝色
            {"id": 2, "name": _("Brown")},  # 褐色
        ]

        theme.update(
            {
                "color": {
                    "default": theme_id.theme_color if theme_id.theme_color in [0, 1, 2] else 0,
                    "colors": theme_color_list,
                },
            }
        )

        session_info.update({"theme": json.loads(json.dumps(theme))})

        project = session_info["project"]
        project.update({"running_days": self.env["project.project"].get_project_running_time()})


        return session_info
