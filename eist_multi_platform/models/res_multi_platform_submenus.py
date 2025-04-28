from odoo import fields, models


class ResMultiPlatformSubMenus(models.Model):
    """
    首页菜单
    """

    _name = "res.multi_platform.submenus"
    _description = "Multi-platform app submenu"
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
    code = fields.Char(string="Code", required=True, translate=False)
    external_id = fields.Char(string="External ID", copy=False)
    parent_ids = fields.Many2many(
        "res.multi_platform.menus",
        "res_multi_platform_menu_submenu_rel",
        "submenu_id",
        "menu_id",
        string="Parent Menu",
        index=True,
    )

    route = fields.Char(string="Route")

    res_model_id = fields.Many2one("ir.model", "Related Model", ondelete="cascade")
    res_model = fields.Char("Related Model Name", related="res_model_id.model", readonly=True, store=True)
    res_id = fields.Many2oneReference("Related Record ID", model_field="res_model")
    res_model_name = fields.Char(related="res_model_id.name")

    sequence = fields.Integer(default=0)
    active = fields.Boolean("Active", default=True)

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company)
