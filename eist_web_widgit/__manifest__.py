# -*- coding: utf-8 -*-

{
    "name": "Web Widgets",
    "category": "Base/Widget",
    "summary": "Widgets",
    "author": "RAIN@EIST",
    "website": "https://eist.com.cn",
    "version": "18.0.0.1",
    "description": """

""",
    "depends": [
        "web",
        "attachment_indexation",
        "eist_erp_base",
    ],
    "external_dependencies": {
        "python": [
            # "pyzbar",
        ],
    },
    "data": [],
    "assets": {
        # "web.assets_common": [
        #     "ierp_web_widgets/static/fonts/fonts.scss",
        # ],
        "web.assets_backend": [
            "eist_web_widgit/static/fonts/fonts.scss",
            "eist_web_widgit/static/src/views/**/*",
        ],
        "web.assets_frontend": [
            # "ierp_web_widgets/static/lib/officetohtml/**/*",
        ],
    },
    "sequence": 500,
    "installable": True,
    "auto_install": ["eist_erp_base"],
    # "auto_install": False,
    "license": "Other proprietary",
    "application": True,
    "installable": True,
}
