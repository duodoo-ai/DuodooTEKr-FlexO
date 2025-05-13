# -*- coding: utf-8 -*-

import json

from odoo import http, fields, _
from odoo.http import Controller, route, request


class ProjectLargeScreen(Controller):

    def _prepare_project_large_screen_layout_values(self):
        """
        准备项目大屏幕布局值
        """
        values = {"projects": []}


        ICP = request.env["ir.config_parameter"].sudo()

        values.update({"title": ICP.get_param("water_supply_pipeline.large_screen_title")})

        provider_info = request.env["res.config.settings"].get_emap_provider_info()
        values.update(
            {
                "provider_info": provider_info,
            }
        )


        # 项目信息
        projects = request.env["project.project"].sudo().get_locations_by_project_ids()
        values.update(
            {
                "projects": projects,
            }
        )

        session_info = request.env["ir.http"].session_info()

        # 语言 和 颜色
        values.update(
            {
                "session_info": session_info,
                "current_lang": session_info["bundle_params"]["lang"],
                "user_context": session_info["user_context"],
                "normal_state_color": session_info["project"]["pipeline"]["normal_state_color"],
                "exception_state_color": session_info["project"]["pipeline"]["exception_state_color"],
                "large_screen_title": session_info["project"]["large_screen"]["title"],
                "large_screen_background_color": session_info["project"]["large_screen"]["background_color"],
            }
        )

        return values

    @route("/project/large_screen", type="http", auth="public", website=True)
    def index(self):
        values = self._prepare_project_large_screen_layout_values()
        # values.update({})
        # print(values)
        response = request.render("odoo_project.project_large_screen", values)
        response.headers["Cache-Control"] = "no-store"
        return response

    @route("/pipeline/large_screen_data", type="json", auth="user")
    def index(self):
        values = self._prepare_project_large_screen_layout_values()

        return values
