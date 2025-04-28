# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime


class ResTheme(models.Model):
    _name = "res.theme"
    _description = "Theme"

    name = fields.Char(
        string="Name",
        copy=False,
        compute="_compute_name",
        store=True,
        index=True,
    )  # 企业应用名称

    company_id = fields.Many2one(
        string="Company", comodel_name="res.company", ondelete="cascade", readonly=True
    )
    user_id = fields.Many2one(string="User", comodel_name="res.users", ondelete="cascade", readonly=True)

    type = fields.Selection(
        string="Type",
        selection=[("user", "User"), ("company", "Company")],
        required=True,
        # compute="_compute_company_type",
        # inverse="_write_company_type",
    )

    # ------------------------------------------------------------
    # 版权的文本内容 ， 文档 / 技术支持 的URL
    # ------------------------------------------------------------
    copyright = fields.Char(related="company_id.copyright", readonly=False)
    doc_url = fields.Char(related="company_id.doc_url", readonly=False)
    support_url = fields.Char(related="company_id.support_url", readonly=False)

    # ------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------
    disable_theme_customizer = fields.Boolean(string="Disable theme customizer", default=False)

    # 1. Main
    # ------------------------------------------------------------
    main_app_load_method = fields.Selection(
        string="Application loading method",
        selection=[
            ("1", "Sidebar Menu"),
            ("2", "Favorites Menu"),
            ("3", "Drawer Menu"),
        ],
        default="1",
        required=True,
    )
    main_display_drawer_menu_button = fields.Boolean(string="Display drawer menu button", default=True)
    main_open_action_in_tabs = fields.Boolean(
        string="Open action in tabs", default=False
    )  # multiple open page in tab
    main_submenu_position = fields.Selection(
        string="Submenu Position",
        selection=[
            ("1", "Header Navbar"),
            ("2", "Sidebar"),
            ("3", "Header Navbar and Sidebar"),
        ],
        default="3",
        required=True,
        readonly=False,
    )

    # 5.Theme color
    # ------------------------------------------------------------
    theme_color = fields.Integer(
        string="Theme color",
        # selection=[
        #     ("red", "Red"),             # 1.红色
        #     ("orange", "Orange"),       # 2.橙色
        #     ("yellow", "Yellow"),       # 3.黄色
        #     ("deep_purple", "Green"),   # 4.绿色
        #     ("blue", "Blue"),           # 5.蓝色
        #     ("indigo", "Indigo"),       # 6.靛蓝色
        #     ("purple", "Purple"),       # 7.紫色
        #     ("grey", "Grey"),           # 8.灰色
        #     ("light", "Light"),         # 9.浅色
        # ],
        default=0,
        required=True,
        readonly=False,
    )  # Red, orange, yellow, green, blue, indigo, purple.

    # 6.Sidebar menu
    # ------------------------------------------------------------
    sidebar_display_number_of_submenus = fields.Boolean(string="Display Number Of Submenus", default=False)
    sidebar_show_minimize_button = fields.Boolean(
        string="Show minimize button",
        default=True,
    )
    sidebar_default_minimized = fields.Boolean(string="Default minimize", default=False)
    sidebar_hover_maximize = fields.Boolean("Hover maximize", default=True)
    sidebar_main_menu_display_icon = fields.Boolean(string="Main menu display icon", default=True)
    sidebar_main_menu_display_arrow = fields.Boolean(string="Main menu display arrow", default=True)
    sidebar_submenu_display_icon = fields.Boolean(string="Submenu display icon", default=True)
    sidebar_submenu_display_arrow = fields.Boolean(string="Submenu display arrow", default=True)

    # 8.Views
    # ------------------------------------------------------------
    display_scroll_top_button = fields.Boolean(string="Display Scroll Top Button", default=True)
    # list_herder_fixed = fields.Boolean(string="List Header Fixed", default=False)
    list_rows_limit = fields.Selection(
        string="Number of rows in the list",
        selection=[
            ("80", "80 rows"),
            ("100", "100 rows"),
            ("120", "120 rows"),
            ("140", "140 rows"),
            ("160", "160 rows"),
            ("180", "180 rows"),
            ("200", "200 rows"),
        ],
        default="80",
        required=True,
    )
    form_chatter_position = fields.Selection(
        string="Form Chatter Position",
        selection=[
            ("1", "Right side of the form"),
            ("2", "Bottom of form"),
        ],
        default="1",
        required=True,
        readonly=False,
    )

    # 9.Footer
    # ------------------------------------------------------------
    display_footer = fields.Boolean(
        string="Display Footer", default=True, help="Show footers only in desktop mode"
    )
    display_footer_support = fields.Boolean(
        string="Display Footer Support", default=True, help="Show support link in footer"
    )
    display_footer_copyright = fields.Boolean(
        string="Display Footer Copyright", default=False, help="Show copyright in footer"
    )
    display_footer_doc = fields.Boolean(
        string="Display Footer Documentation", default=False, help="Show Documentation in footer"
    )
    display_footer_version = fields.Boolean(
        string="Display Footer Version", default=False, help="Show Version in footer"
    )

    @api.depends("company_id", "user_id", "type")
    def _compute_name(self):
        for theme in self:
            labels = dict(self.fields_get(allfields=["type"])["type"]["selection"])[theme.type]  # type: ignore
            if theme.company_id:  # type: ignore
                theme.name = "%s:%s" % (labels, theme.company_id.name)  # type: ignore
            else:
                theme.name = "%s:%s" % (labels, theme.user_id.name)  # type: ignore

    def _get_or_create_theme(self, id, type):
        """
        通过id和type获取或者创建theme
        """
        domain = []
        vals = {}
        if type == "company":
            domain = [("company_id", "=", id), ("type", "=", "company")]
            vals = {"company_id": id, "type": "company"}
        elif type == "user":
            domain = [("user_id", "=", id), ("type", "=", "user")]
            vals = {"user_id": id, "type": "user"}
        theme = self.search(domain, limit=1)

        if not theme:
            theme = self.create(vals)

        return theme
