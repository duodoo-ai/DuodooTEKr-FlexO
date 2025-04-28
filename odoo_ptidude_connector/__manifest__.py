# -*- coding: utf-8 -*-
{
    'name': "Odoo SKF Phoemix API Connector",

    'summary': """
    给Odoo与SKF Phoemix API平台提供连接，以完成数据从SKF Phoemix API采集到Odoo平台
    """,

    'description': """API平台提供接口以完成数据从SKF Observer Phoemix API诊断平台采集到Odoo，以完成后续维检操作
                    更多支持：
                    18951631470
                    zou.jason@qq.com
                    """,

    'author': "Jason Zou",
    "website": "-",

    'category': 'Internet of Things (IoT)',
    'version': '1.0',

    'depends': ['base', 'mail', 'odoo_base', 'odoo_phoenix_maintenance', 'maintenance'],

    'data': [
        'data/phoenix_cron.xml',
        'data/phoenix_data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/phoenix_token_views.xml',
        'views/configurator_views.xml',
        # 'views/dynamic_list_view_inherit.xml',
        'views/phoenix_menu_views.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
