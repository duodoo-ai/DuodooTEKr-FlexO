# -*- coding: utf-8 -*-

import base64
import datetime

from odoo import models, fields, api, tools, _
from odoo.tools import html2plaintext, file_open, ormcache


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_favicon(self, original=False):
        with file_open("web/static/img/favicon.ico", "rb") as file:
            return base64.b64encode(file.read())

    def _get_square_logo(self, original=False):
        with file_open("eist_web_theme/static/img/square_logo.png", "rb") as file:
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
    square_logo_web = fields.Binary(
        compute="_compute_square_logo_web", store=True, attachment=False
    )

    # ------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------
    theme_id = fields.Many2one(
        "res.theme",
        string="Theme",
        store=True,
        domain="[('company_id', '=', id)]",
    )
    disable_theme_customizer = fields.Boolean(
        string="Disable theme customizer",
        related="theme_id.disable_theme_customizer",
        readonly=False,
    )

    # 1. Main
    # ------------------------------------------------------------
    main_app_load_method = fields.Selection(
        related="theme_id.main_app_load_method",
        readonly=False,
    )
    main_display_drawer_menu_button = fields.Boolean(
        related="theme_id.main_display_drawer_menu_button",
        readonly=False,
    )
    main_submenu_position = fields.Selection(
        related="theme_id.main_submenu_position",
        readonly=False,
    )
    main_open_action_in_tabs = fields.Boolean(
        related="theme_id.main_open_action_in_tabs", readonly=False
    )

    # 3.Theme color
    # ------------------------------------------------------------
    theme_color = fields.Integer(related="theme_id.theme_color", readonly=False)

    # 4.Sidebar menu
    # ------------------------------------------------------------
    sidebar_display_number_of_submenus = fields.Boolean(
        related="theme_id.sidebar_display_number_of_submenus", readonly=False
    )

    sidebar_show_minimize_button = fields.Boolean(
        related="theme_id.sidebar_show_minimize_button", readonly=False
    )
    sidebar_default_minimized = fields.Boolean(
        related="theme_id.sidebar_default_minimized", readonly=False
    )
    sidebar_hover_maximize = fields.Boolean(
        related="theme_id.sidebar_hover_maximize", readonly=False
    )
    sidebar_main_menu_display_icon = fields.Boolean(
        related="theme_id.sidebar_main_menu_display_icon", readonly=False
    )
    sidebar_main_menu_display_arrow = fields.Boolean(
        related="theme_id.sidebar_main_menu_display_arrow", readonly=False
    )
    sidebar_submenu_display_icon = fields.Boolean(
        related="theme_id.sidebar_submenu_display_icon", readonly=False
    )
    sidebar_submenu_display_arrow = fields.Boolean(
        related="theme_id.sidebar_submenu_display_arrow", readonly=False
    )


    # 8.Views
    # ------------------------------------------------------------
    display_scroll_top_button = fields.Boolean(
        related="theme_id.display_scroll_top_button", readonly=False
    )
    # list_herder_fixed = fields.Boolean(
    #     related="theme_id.list_herder_fixed", readonly=False
    # )
    list_rows_limit = fields.Selection(
        related="theme_id.list_rows_limit", readonly=False
    )
    form_chatter_position = fields.Selection(
        related="theme_id.form_chatter_position", readonly=False
    )

    # 9.Footer
    # ------------------------------------------------------------
    display_footer = fields.Boolean(
        related="theme_id.display_footer", readonly=False
    )
    display_footer_support = fields.Boolean(
        related="theme_id.display_footer_support", readonly=False
    )
    display_footer_copyright = fields.Boolean(
        related="theme_id.display_footer_copyright", readonly=False
    )
    display_footer_doc = fields.Boolean(
        related="theme_id.display_footer_doc", readonly=False
    )
    display_footer_version = fields.Boolean(
        related="theme_id.display_footer_version", readonly=False
    )

    # ------------------------------------------------------------
    # 用户下拉菜单
    # ------------------------------------------------------------
    menuitem_id = fields.Many2one(
        "res.user.menuitems",
        string="User menu items",
        store=True,
        domain="[('company_id', '=', id)]",
    )
    enable_odoo_account = fields.Boolean(
        related="menuitem_id.enable_odoo_account", readonly=False
    )
    enable_lock_screen = fields.Boolean(
        related="menuitem_id.enable_lock_screen", readonly=False
    )
    lock_screen_state_storage_mode = fields.Selection(
        string="Lock screen state storage mode",
        selection=[
            ("1", "Use browser's local storage"),
            ("2", "Use database"),
        ],
        default="1",
    )
    enable_developer_tool = fields.Boolean(
        related="menuitem_id.enable_developer_tool", readonly=False
    )
    enable_documentation = fields.Boolean(
        related="menuitem_id.enable_documentation", readonly=False
    )
    enable_support = fields.Boolean(
        related="menuitem_id.enable_support", readonly=False
    )

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

    # ------------------------------------------------------------
    # 版权的文本内容 ， 文档 / 技术支持 的URL
    # ------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        # add default favicon
        for vals in vals_list:
            if not vals.get("favicon"):
                vals["favicon"] = self._get_favicon()
        self.env.registry.clear_cache()

        companies = super().create(vals_list)
        return companies

    @api.model_create_multi
    def create(self, vals_list):
        """
        创建新公司时，创建主题 和 用户菜单项目
        """
        companies = super(ResCompany, self).create(vals_list)
        for new_company in companies:
            new_company.theme_id = (  # type: ignore
                self.env["res.theme"]
                .sudo()
                ._get_or_create_theme(new_company.id, "company")  # type: ignore
            )

            new_company.menuitem_id = (  # type: ignore
                self.env["res.user.menuitems"]
                .sudo()
                ._get_or_create_menuitems(new_company.id)  # type: ignore
            )

        return companies

    @api.depends("square_logo")
    def _compute_square_logo_web(self):
        for company in self:
            img = company.square_logo
            company.square_logo_web = img and base64.b64encode(
                tools.image_process(base64.b64decode(img), size=(46, 0))
            )
