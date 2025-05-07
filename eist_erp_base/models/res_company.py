# -*- coding: utf-8 -*-

import base64
import datetime

from odoo import models, fields, api, tools, _
from odoo.tools import html2plaintext, file_open, ormcache


class Company(models.Model):
    _inherit = "res.company"

    fax = fields.Char(related="partner_id.fax", store=True, readonly=False)

    def _get_favicon(self):
        with file_open("eist_erp_base/static/img/square_logo.png", "rb") as file:
            return base64.b64encode(file.read())

    def _get_square_logo(self):
        with file_open("eist_erp_base/static/img/square_logo.png", "rb") as file:
            return base64.b64encode(file.read())

    favicon = fields.Binary(
        string="Company Favicon",
        help="This field holds the image used to display a favicon for a given company.",
        default=_get_favicon,
    )
    square_logo = fields.Binary(
        default=_get_square_logo,
        # related="partner_id.image_1920",
        string="Company Square Logo",
        readonly=False,
    )
    square_logo_web = fields.Binary(compute="_compute_square_logo_web", store=True, attachment=False)


    def _get_default_copyright(self):
        """
        年份© 公司名称
        """
        return "%s© %s" % (datetime.datetime.today().year, (self.name if self.name else "EIST"))  # type: ignore

    copyright = fields.Char(string="Copyright", default=_get_default_copyright)
    doc_url = fields.Char(
        string="Documentation URL", default="https://docs.eist.com.cn"
    )
    support_url = fields.Char(string="Support URL", default="https://eist.com.cn/")


    @api.depends("square_logo")
    def _compute_square_logo_web(self):
        for company in self:
            img = company.square_logo
            company.square_logo_web = img and base64.b64encode(
                tools.image_process(base64.b64decode(img), size=(46, 0))
            )
