# -*- coding: utf-8 -*-

import json
import logging
from pickle import TRUE


from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.web.controllers.home import Home as WebHome # type: ignore
from odoo.addons.web.controllers.utils import is_user_internal, ensure_db # type: ignore


class Home(WebHome):

    @http.route("/web/lang/toggle", type="json", auth="user")
    def toggle_web_lang(self, lang):
        uid = dict(request.context)["uid"]
        if not uid:
            return False

        user = request.env["res.users"].browse(uid)
        try:
            user.sudo().write({"lang": lang["code"]})
        except Exception as e:
            print(str(e))
            return False
        else:
            session_info = request.env["ir.http"].session_info()
            session_info["current_lang"] = lang
            return True
