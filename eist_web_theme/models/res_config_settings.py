# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # ------------------------------------------------------------
    # 品牌设置
    # ------------------------------------------------------------
    system_name = fields.Char(
        string="System Name",
        readonly=False,
        config_parameter="eist_erp.system_name",
        default="EIST ERP",
    )
    display_company_name = fields.Boolean(
        string="Display Company Name",
        default=False,
        config_parameter="eist_erp.display_company_name",
    )
    full_system_name = fields.Char(
        config_parameter="eist_erp.full_system_name", compute="_compute_full_system_name"
    )
    logo = fields.Binary(related="company_id.logo", readonly=False)
    square_logo = fields.Binary(related="company_id.square_logo", readonly=False)
    favicon = fields.Binary(related="company_id.favicon", readonly=False)
    copyright = fields.Char(related="company_id.copyright", readonly=False)
    doc_url = fields.Char(related="company_id.doc_url", readonly=False)
    support_url = fields.Char(related="company_id.support_url", readonly=False)

    # ------------------------------------------------------------
    # 主题定制
    # ------------------------------------------------------------
    # module_ierp_web_theme_mail = fields.Boolean("Discuss Theme")
    # module_ierp_web_theme_spreadsheet = fields.Boolean("Spreadsheet Theme")
    disable_theme_customizer = fields.Boolean(
        related="company_id.disable_theme_customizer", readonly=False
    )

    # 1. Main
    # ------------------------------------------------------------
    main_app_load_method = fields.Selection(
        related="company_id.main_app_load_method", readonly=False
    )
    main_display_drawer_menu_button = fields.Boolean(
        related="company_id.main_display_drawer_menu_button", readonly=False
    )
    main_submenu_position = fields.Selection(
        related="company_id.main_submenu_position", readonly=False
    )
    main_open_action_in_tabs = fields.Boolean(
        related="company_id.main_open_action_in_tabs", readonly=False
    )

    # 3.Theme color
    # ------------------------------------------------------------
    theme_color = fields.Integer(related="company_id.theme_color", readonly=False)

    # 4.Sidebar menu
    # ------------------------------------------------------------
    sidebar_display_number_of_submenus = fields.Boolean(
        related="company_id.sidebar_display_number_of_submenus", readonly=False
    )
    sidebar_show_minimize_button = fields.Boolean(
        related="company_id.sidebar_show_minimize_button", readonly=False
    )
    sidebar_default_minimized = fields.Boolean(
        related="company_id.sidebar_default_minimized", readonly=False
    )
    sidebar_hover_maximize = fields.Boolean(
        related="company_id.sidebar_hover_maximize", readonly=False
    )
    sidebar_main_menu_display_icon = fields.Boolean(
        related="company_id.sidebar_main_menu_display_icon", readonly=False
    )
    sidebar_main_menu_display_arrow = fields.Boolean(
        related="company_id.sidebar_main_menu_display_arrow", readonly=False
    )
    sidebar_submenu_display_icon = fields.Boolean(
        related="company_id.sidebar_submenu_display_icon", readonly=False
    )
    sidebar_submenu_display_arrow = fields.Boolean(
        related="company_id.sidebar_submenu_display_arrow", readonly=False
    )


    # 8.Views
    # ------------------------------------------------------------
    display_scroll_top_button = fields.Boolean(
        related="company_id.display_scroll_top_button", readonly=False
    )
    # list_herder_fixed = fields.Boolean(
    #     related="company_id.list_herder_fixed", readonly=False
    # )
    list_rows_limit = fields.Selection(
        related="company_id.list_rows_limit", readonly=False
    )
    form_chatter_position = fields.Selection(
        related="company_id.form_chatter_position", readonly=False
    )

    # 9.Footer
    # ------------------------------------------------------------
    display_footer = fields.Boolean(
        related="company_id.display_footer", readonly=False
    )
    display_footer_support = fields.Boolean(
        related="company_id.display_footer_support", readonly=False
    )
    display_footer_copyright = fields.Boolean(
        related="company_id.display_footer_copyright", readonly=False
    )
    display_footer_doc = fields.Boolean(
        related="company_id.display_footer_doc", readonly=False
    )
    display_footer_version = fields.Boolean(
        related="company_id.display_footer_version", readonly=False
    )


    # ------------------------------------------------------------
    # 登录页面设置
    # ------------------------------------------------------------
    login_page_display_logo = fields.Boolean(
        string="Login page displays logo",
        config_parameter="eist_erp.login_page_display_logo",
    )
    login_page_login_as_username = fields.Boolean(
        string="Login page replaces the email text with a username",
        config_parameter="eist_erp.login_as_username",
    )
    login_page_display_login_as_superuser = fields.Boolean(
        string="Login page displays 'Log in as superuser' button",
        config_parameter="eist_erp.login_as_superuser_button",
    )
    login_page_display_db_management = fields.Boolean(
        string="Login page displays database management",
        config_parameter="eist_erp.login_page_db_management",
    )
    login_page_display_support = fields.Boolean(
        string="Login page displays technical support",
        config_parameter="eist_erp.login_page_support",
    )
    login_page_support_text = fields.Char(
        string="Login page technical support text",
        config_parameter="eist_erp.login_page_support_txet",
        default="EIST",
    )
    login_page_support_url = fields.Char(
        string="Login page technical support link",
        config_parameter="eist_erp.login_page_support_url",
        default="https://eist.com.cn/support",
    )

    signup_page_email_required = fields.Boolean(
        string="Signup page email required",
        config_parameter="eist_erp.signup_email_required",
    )

    @api.depends("system_name", "display_company_name")
    def _compute_full_system_name(self):
        for record in self:
            main_company = self.sudo().env.ref("base.main_company")
            if record.display_company_name:
                record.full_system_name = "%s - %s" % (
                    main_company.name,
                    record.system_name,
                )
            else:
                record.full_system_name = record.system_name
