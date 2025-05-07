# -*- coding: utf-8 -*-

{
    "name": "Website(EIST)",
    "category": "Website/Website",
    "sequence": 20,
    "summary": "Enterprise website builder",
    "description": """
Enterprise website builder
====================
- Filing for the Chinese website
- Customize support information
    """,
    "author": "RAIN@EIST",
    "website": "https://eist.com.cn",
    "version": "18.0.0.1",
    "depends": [
        "web_editor",
        "portal",
        "website",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "views/res_config_settings_views.xml",
        "views/webclient_templates.xml",
        "views/snippets/snippets.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": ["website"],
    "assets": {
        "web.assets_frontend": [],
        "web.assets_frontend_minimal": [],
        "web.assets_frontend_lazy": [],
        "web._assets_primary_variables": [],
        "web._assets_secondary_variables": [],
        "web.assets_tests": [],
        "web.assets_backend": [
            "eist_website/static/src/webclient/**/*",
        ],
        "web.assets_web_dark": [],
        "web._assets_frontend_helpers": [],
        "web_editor.assets_wysiwyg": [],
        "website.assets_wysiwyg": [],
        "website.assets_all_wysiwyg": [],
        "website.backend_assets_all_wysiwyg": [],
        "web_editor.assets_media_dialog": [],
        "website.assets_editor": [],
    },
    "uninstall_hook": "uninstall_hook",
    "license": "Other proprietary",
}
