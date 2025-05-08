# -*- coding: utf-8 -*-

{
    "name": "ZYfire Theme",
    "author": "RAIN@EIST",
    "website": "https://eist.com.cn",
    "category": "ZYfire/Theme",
    "version": "18.0.0.1",
    "description": """""",
    "depends": ["eist_web_theme","rtx_project"],
    "excludes": [],
    "auto_install": False,
    "data": [],
    "assets": {},
    "license": "Other proprietary",
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "application": True,
    "installable": True,
    "auto_install": ["eist_web_theme","rtx_project"],
    "post_init_hook": "post_init_hook",  # 安装后执行的方法
    "assets": {
        "web._assets_primary_variables": [
            (
                "replace",
                "eist_web_theme/static/src/scss/primary_variables.scss",
                "zyfire_theme/static/src/scss/primary_variables.scss",
            ),
        ],
        "web.assets_backend": [
            (
                "after",
                "eist_web_theme/static/src/core/theme_colorlist/theme_colorlist.js",
                "zyfire_theme/static/src/core/theme_colorlist/theme_colorlist.js",
            ),
            (
                "replace",
                "eist_web_theme/static/src/core/theme_colorlist/theme_colorlist.scss",
                "zyfire_theme/static/src/core/theme_colorlist/theme_colorlist.scss",
            ),
            (
                "after",
                "eist_web_theme/static/src/views/fields/theme_color_picker/theme_color_picker.js",
                "zyfire_theme/static/src/views/fields/theme_color_picker/theme_color_picker.js",
            ),
            (
                "after",
                "eist_web_theme/static/src/webclient/webclient_theme.scss",
                "zyfire_theme/static/src/webclient/webclient_theme.scss",
            ),
            "zyfire_theme/static/src/webclient/navbar/**/*",
            "zyfire_theme/static/src/webclient/sidebar_menu/**/*",
            "zyfire_theme/static/src/webclient/footer/**/*",
        ]
    },
}
