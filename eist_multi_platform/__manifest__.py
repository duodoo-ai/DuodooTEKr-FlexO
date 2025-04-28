# -*- coding: utf-8 -*-


{
    "name": "Multi platform access",
    "sequence": 1,
    "category": "Base/Multi platform",
    "summary": "Multi-platform application access",
    "author": "RAIN@EIST",
    "website": "https://eist.com.cn",
    "version": "18.0.0.1",
    "description": """
This module provides the core functionality of Multi-platform.
        """,
    "depends": [
        "base_setup",
        "web",
        "portal",
        "eist_erp_base",
    ],
    "excludes": [],
    "external_dependencies": {
        "python": [
            "pefile",
        ],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "data/menus_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_multi_platform_menus_views.xml",
        "views/res_multi_platform_submenus_views.xml",
        "views/res_multi_platform_apps_views.xml",
        "views/multi_platform_menuitem.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "eist_multi_platform/static/libs/material-icons/**/*",
            # "eist_multi_platform/static/libs/material-icons/css/material-icons.css",
            # "eist_multi_platform/static/libs/material-icons/scss/material-icons.scss",
            "eist_multi_platform/static/src/**/*",
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
}
