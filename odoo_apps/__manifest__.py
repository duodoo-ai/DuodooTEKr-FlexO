# -*- coding: utf-8 -*-

{
    "name": "Odoo Extend Base Module(RTX)",
    "version": "18.0.0.1",
    'description': """The kernel of Odoo, needed for all installation.
                    More Support：
                    18951631470
                    zou.jason@qq.com
                    """,
    'author': "Jason Zou",
    "website": "-",
    'category': 'Internet of Things (IoT)',
    "sequence": 45,
    "summary": "The kernel of Odoo, needed for all installation",
    "depends": [
        "base",
    ],
    'data': [
        'views/menu_hide_views.xml',
        'views/base_menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
