# -*- coding: utf-8 -*-

{
    "name": "EIST ERP Base",
    "sequence": -1,
    "summary": "EIST ERP",
    "website": "https://eist.com.cn",
    "author": "RAIN@EIST",
    "category": "Base/Core",
    "version": "18.0.0.1",
    "description": """""",
    "depends": ["web", "base_setup"],
    "excludes": [
        "web_enterprise",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "data": [
        "security/core_security.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/webclient_templates.xml",
        "views/res_config_settings_views.xml",
        "views/configurator_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "eist_erp_base/static/libs/bootstrap-icons/font/bootstrap-icons.min.css",
            "eist_erp_base/static/src/views/**/*",
            "eist_erp_base/static/src/webclient/**/*",
            # "https://pyscript.net/latest/pyscript.css",
            # "https://pyscript.net/latest/pyscript.js",
        ],
        "web.assets_frontend": [
            # "https://pyscript.net/latest/pyscript.css",
            # "https://pyscript.net/latest/pyscript.js",
        ],
    },
    "license": "Other proprietary",
    "post_init_hook": "post_init_hook",  # 安装后执行的方法
    "uninstall_hook": "uninstall_hook",  # 卸载后执行的方法
}
