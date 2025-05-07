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
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "views/mail_menus.xml",
        "views/res_config_settings_views.xml",
        "views/webclient_templates.xml",
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
            "eist_web_theme/static/src/webclient/drawer_menu/drawer_menu_background.scss",
            "eist_web_theme/static/src/webclient/navbar/navbar.scss",
        ],
        "web.assets_backend": [
            # 主题样式文件
            "eist_web_theme/static/src/webclient/webclient_theme.scss",
            # 其他资源
            "eist_web_theme/static/src/model/**/*",
            "eist_web_theme/static/src/webclient/**/*.scss",
            "eist_web_theme/static/src/views/**/*.scss",
            "eist_web_theme/static/src/core/**/*",
            "eist_web_theme/static/src/webclient/**/*.js",
            "eist_web_theme/static/src/webclient/**/*.xml",
            "eist_web_theme/static/src/views/**/*.js",
            "eist_web_theme/static/src/views/**/*.xml",
            ("remove", "eist_web_theme/static/src/views/pivot/**"),
            # 不要在浅色模式中包含深色模式文件
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
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "license": "Other proprietary",
    "bootstrap": True,
    "application": True,
    "installable": True,
    "auto_install": ["eist_erp_base"],
}
