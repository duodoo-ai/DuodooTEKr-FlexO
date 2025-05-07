# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _

import base64


class Website(models.Model):
    _inherit = "website"

    # ------------------
    # ​ICP备案编号
    # "ICP Filing Number"​​（最常用，官方推荐）
    #
    # ​ICP许可证编号
    # "ICP License Number"​​（适用于商业性网站的许可证，如ICP证）
    # ​​"ICP Operating License Number"​​（更完整，强调经营性许可）
    #
    # 官方英文材料（如工信部）统一使用 ​​"ICP Filing"​​ 和 ​​"ICP License"​。
    # ------------------
    cn_icp_number = fields.Char(string="Internet Content Provider Filing Number/License Number")  # 工信部备案
    cn_psb_number = fields.Char(string="Public Security Bureau (PSB) Internet Filing Number")  # 公安机关备案


    def _default_support_info_logo(self):
        with tools.file_open('eist_website/static/src/img/tiny_support_logo.png', 'rb') as f:
            return base64.b64encode(f.read())


    customize_support_info = fields.Boolean(
        string="Customize support information",
        default=False,
        help="If True, the support information will be customized",
    )  # 是否自定义技术支持信息

    support_info_logo = fields.Binary(
        string="Website Support Logo",
        default=_default_support_info_logo,
        help="A tiny logo for customizing technical support information",
    )  # 小logo
    support_info_text = fields.Char(
        string="Technical support text",
        default="EIST",
    )  # 技术支持信息文本

    support_info_url = fields.Char(
        string="Technical support URL",
        default="https://eist.com.cn/support",
    )  # 技术支持信息链接
