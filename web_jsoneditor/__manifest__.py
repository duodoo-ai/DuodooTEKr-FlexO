# -*- coding: utf-8 -*-

{
    "name": "Web Json Editor",
    "category": "Extra Tools",
    "version": "18.0.0.1",
    "author": "rain.wen@eist.com.cn",
    "website": "https://eist.com.cn",
    "summary": "Web JSON Editor is used to view, edit, format and validate JSON. It has multiple modes, such as tree editor, code editor and plain text editor. ",
    "description": """

    """,
    "depends": [
        "web",
    ],
    "auto_install": True,
    "application": True,
    "installable": True,
    "images": ["images/main_screenshot.gif"],
    "currency": "EUR",
    "price": 20,
    "assets": {
        "web.assets_backend": [
            "web_jsoneditor/static/src/views/**/*",
        ],
    },
    "external_dependencies": {
        "python": [],
    },
    "license": "LGPL-3",
}
