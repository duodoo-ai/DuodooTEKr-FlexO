# -*- coding: utf-8 -*-

import ast
import json
from odoo import models, _
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _post_logout(cls):
        request.future_response.set_cookie("color_scheme", max_age=0)

    def webclient_rendering_context(self):
        """
        覆盖社区版以防止不必要的load_menus请求
        """
        return {
            "session_info": self.session_info(),
        }

    def session_info(self):
        ICP = self.env["ir.config_parameter"].sudo()
        current_user = self.env.user
        current_user_company = current_user.company_id

        session_info = super(Http, self).session_info()

        # -------------------------------------------------------
        # 品牌
        # -------------------------------------------------------
        system_name = ICP.get_param("eist_erp.system_name", default="EIST ERP")
        display_company_name = ICP.get_param("eist_erp.display_company_name", default=False)

        if type(display_company_name) == str:
            display_company_name = bool(ast.literal_eval(display_company_name))

        session_info["brand"] = {
            "system_name": system_name,
            "display_company_name": display_company_name,
        }


        return session_info
