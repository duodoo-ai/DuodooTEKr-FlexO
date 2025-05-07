# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

from werkzeug import urls


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 备案信息
    website_cn_icp_number = fields.Char(
        related="website_id.cn_icp_number", readonly=False, string="ICP Filing Number/License Number"
    )  # 工信部备案
    website_cn_psb_number = fields.Char(
        related="website_id.cn_psb_number", readonly=False, string="PSB Filing Number"
    )  # 公安机关备案

    # 自定义支持信息
    customize_support_info = fields.Boolean(
        related="website_id.customize_support_info",
        readonly=False,
    )  # 自定义技术支持信息
    support_info_logo = fields.Binary(related="website_id.support_info_logo", readonly=False)  # 技术支持信息logo
    support_info_text = fields.Char(
        related="website_id.support_info_text",
        readonly=False,
    )  # 技术支持信息文本

    support_info_url = fields.Char(
        related="website_id.support_info_url",
        readonly=False,
    )  # 技术支持信息链接
