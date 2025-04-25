# -*- coding: utf-8 -*-
{
    'name': "Odoo DTU Extend(RTX)",

    'summary': """
        给Odoo与DTU平台连接，以完成数据从DTU网关采集数据到Odoo平台，支持多DTU接口数据采集
    """,

    'description': """给Odoo与平台连接，以完成数据从DTU网关采集数据到Odoo平台，以完成后续维检操作
                    更多支持：
                    18951631470
                    zou.jason@qq.com
                    """,

    'author': "Jason Zou",
    "website": "-",

    'category': 'Internet of Things (IoT)',
    'version': '1.0',

    'depends': ['base', 'mail', 'iot'],

    'data': [
        'security/ir.model.access.csv',
        'views/dtu_data_views.xml',
        'views/dtu_menu_views.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
