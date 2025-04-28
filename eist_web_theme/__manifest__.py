# -*- coding: utf-8 -*-

{
    "name": "Web Theme",
    "author": "RAIN@EIST",
    "website": "https://eist.com.cn",
    "category": "Base/Theme",
    "version": "18.0.0.1",
    "sequence": 0,
    "description": """
EIST Web Client.
==========================
This module modifies web plugins to provide excellent design and responsiveness.
        """,
    "depends": ["eist_erp_base", "mail", "auth_signup"],
    "excludes": [
        "web_enterprise",
    ],
    "auto_install": ["eist_erp_base"],
    "data": [
        "security/ir.model.access.csv",
        "views/mail_menus.xml",
        # "data/ir_config_parameter.xml",
        # "data/res_theme_data.xml",
        # "data/res_company_data.xml",
        "views/res_config_settings_views.xml",
        "views/webclient_templates.xml",
        # "views/auth_signup_templates.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            ("replace", "web/static/fonts/fonts.scss", "eist_web_theme/static/fonts/fonts.scss"),
        ],
        "web._assets_primary_variables": [
            (
                "after",
                "web/static/src/scss/primary_variables.scss",
                "eist_web_theme/static/src/**/*.variables.scss",
            ),
            (
                "before",
                "web/static/src/scss/primary_variables.scss",
                "eist_web_theme/static/src/scss/primary_variables.scss",
            ),
        ],
        "web._assets_secondary_variables": [
            (
                "before",
                "web/static/src/scss/secondary_variables.scss",
                "eist_web_theme/static/src/scss/secondary_variables.scss",
            ),
        ],
        "web._assets_backend_helpers": [
            (
                "before",
                "web/static/src/scss/bootstrap_overridden.scss",
                "eist_web_theme/static/src/scss/bootstrap_overridden.scss",
            ),
        ],
        "web.assets_frontend": [
            "eist_web_theme/static/src/webclient/drawer_menu/drawer_menu_background.scss",  # used by login page
            "eist_web_theme/static/src/webclient/navbar/navbar.scss",
        ],
        "web.assets_backend": [
            "eist_web_theme/static/src/model/**/*",
            "eist_web_theme/static/src/webclient/**/*.scss",
            "eist_web_theme/static/src/views/**/*.scss",
            "eist_web_theme/static/src/core/**/*",
            "eist_web_theme/static/src/webclient/**/*.js",
            (
                "after",
                "web/static/src/views/list/list_renderer.xml",
                "eist_web_theme/static/src/views/list/list_renderer_desktop.xml",
            ),
            "eist_web_theme/static/src/webclient/**/*.xml",
            "eist_web_theme/static/src/views/**/*.js",
            "eist_web_theme/static/src/views/**/*.xml",
            ("remove", "eist_web_theme/static/src/views/pivot/**"),
            # Don't include dark mode files in light mode
            ("remove", "eist_web_theme/static/src/**/*.dark.scss"),
            "eist_web_theme/static/src/chatter/**/*",
            "eist_web_theme/static/src/components/**/*",
        ],
        "web.assets_backend_lazy": [
            "eist_web_theme/static/src/views/pivot/**",
        ],
        "web.assets_backend_lazy_dark": [
            ("include", "web.dark_mode_variables"),
            # web._assets_backend_helpers
            (
                "before",
                "eist_web_theme/static/src/scss/bootstrap_overridden.scss",
                "eist_web_theme/static/src/scss/bootstrap_overridden.dark.scss",
            ),
            (
                "after",
                "web/static/lib/bootstrap/scss/_functions.scss",
                "eist_web_theme/static/src/scss/bs_functions_overridden.dark.scss",
            ),
        ],
        "web.assets_web": [
            ("replace", "web/static/src/main.js", "eist_web_theme/static/src/main.js"),
        ],
        # ========= Dark Mode =========
        "web.dark_mode_variables": [
            # web._assets_primary_variables
            (
                "before",
                "eist_web_theme/static/src/scss/primary_variables.scss",
                "eist_web_theme/static/src/scss/primary_variables.dark.scss",
            ),
            (
                "before",
                "eist_web_theme/static/src/**/*.variables.scss",
                "eist_web_theme/static/src/**/*.variables.dark.scss",
            ),
            # web._assets_secondary_variables
            (
                "before",
                "eist_web_theme/static/src/scss/secondary_variables.scss",
                "eist_web_theme/static/src/scss/secondary_variables.dark.scss",
            ),
        ],
        "web.assets_web_dark": [
            ("include", "web.dark_mode_variables"),
            # web._assets_backend_helpers
            (
                "before",
                "eist_web_theme/static/src/scss/bootstrap_overridden.scss",
                "eist_web_theme/static/src/scss/bootstrap_overridden.dark.scss",
            ),
            (
                "after",
                "web/static/lib/bootstrap/scss/_functions.scss",
                "eist_web_theme/static/src/scss/bs_functions_overridden.dark.scss",
            ),
            # assets_backend
            "eist_web_theme/static/src/**/*.dark.scss",
        ],
    },
    "post_init_hook": "post_init_hook",  # 安装后执行的方法
    "uninstall_hook": "uninstall_hook",  # 卸载后执行的方法
    "license": "Other proprietary",
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "application": True,
    "installable": True,
}
