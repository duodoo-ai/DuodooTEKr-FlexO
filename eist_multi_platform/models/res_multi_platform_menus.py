# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ResMultiPlatformMenus(models.Model):
    """
    首页菜单
    """

    _name = "res.multi_platform.menus"
    _description = "Multi-platform app menu"
    _order = "sequence asc"

    name = fields.Char(string="Name", required=True, translate=True)  # 名称
    code = fields.Char(string="Code", required=True, translate=False)  # 代码
    image_icon = fields.Image(
        string="Image Icon",
        copy=False,
        store=True,
        attachment=False,
        readonly=False,
        max_width=90,
        max_height=90,
    )
    char_icon = fields.Char(
        string="Character Icon",
        copy=False,
        default="home",
        translate=False,
        required=True,
    )  # 字符图标
    icon_type = fields.Selection(
        [
            ("character", "Character"),
            ("image", "Image"),
        ],
        string="Icon Type",
        default="",
        required=True,
    )
    child_ids = fields.Many2many(
        "res.multi_platform.submenus",
        "res_multi_platform_menu_submenu_rel",
        "menu_id",
        "submenu_id",
        string="Child Menus",
    )  # 子菜单
    route = fields.Char(string="Route")

    group_ids = fields.Many2many(
        "res.groups", "pda_menu_group_rel", "pm_id", "gid", string="Access Groups"
    )  # 访问组
    sequence = fields.Integer(default=0)  # 优先级
    active = fields.Boolean("Active", default=True)  # 是否激活
    display_in_bottom_app_bar = fields.Boolean(
        default=False,
        string="Display in bottom app bar",
        help="If true, the menu will be displayed in the bottom application bar of the mobile terminal application. By default, four application menus are displayed, which can be set in the configuration.",
    )  # 是否显示在底部导航栏

    _sql_constraints = [
        ("name_uniq", "unique (name)", _("A record of that name already exists.")),
        ("code_uniq", "unique (code)", _("A record of the code already exists")),
    ]
