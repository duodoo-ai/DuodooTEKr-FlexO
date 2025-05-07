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
        config_parameter="eist_erp_theme.login_page_display_logo",
    ) # 登录页面显示logo
    login_page_login_as_username = fields.Boolean(
        string="Login page replaces the email text with a username",
        config_parameter="eist_erp_theme.login_as_username",
    ) # 登录页面替换邮箱文本为用户名
    login_page_display_login_as_superuser = fields.Boolean(
        string="Login page displays 'Log in as superuser' button",
        config_parameter="eist_erp_theme.login_as_superuser_button",
    ) # 登录页面显示“以超级用户登录”按钮
    login_page_display_db_management = fields.Boolean(
        string="Login page displays database management",
        config_parameter="eist_erp_theme.login_page_db_management",
    ) # 登录页面显示“数据库管理”按钮
    login_page_display_support = fields.Boolean(
        string="Login page displays technical support",
        config_parameter="eist_erp_theme.login_page_support",
    ) # 登录页面显示“技术支持”按钮
    login_page_support_text = fields.Char(
        string="Login page technical support text",
        config_parameter="eist_erp_theme.login_page_support_txet",
        default="EIST",
    ) # 登录页面技术支持文本
    login_page_support_url = fields.Char(
        string="Login page technical support link",
        config_parameter="eist_erp_theme.login_page_support_url",
        default="https://eist.com.cn/support",
    ) # 登录页面技术支持链接

    signup_page_email_required = fields.Boolean(
        string="Signup page email required",
        config_parameter="eist_erp_theme.signup_email_required",
    ) # 注册页面邮箱必填


