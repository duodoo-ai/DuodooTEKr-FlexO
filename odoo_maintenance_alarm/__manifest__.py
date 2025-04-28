# -*- coding: utf-8 -*-
{
    'name': "Odoo Smart Diagnostic Alarm Module",

    'summary': """
    Odoo Phoemix Alarm Module 声光告警模组 取告警数据推送至声光报警器进行告警动作
    """,

    'description': """Odoo Phoemix Alarm Module 声光告警模组 取告警数据推送至声光报警器进行告警动作
                    更多支持：
                    18951631470
                    zou.jason@qq.com
                    """,

    'author': "Jason Zou",
    "website": "-",

    'category': 'Internet of Things (IoT)',
    'version': '1.0',

    'depends': ['base', 'mail', 'maintenance', 'rtx_maintenance'],

    'data': [
        'data/phoenix_alarm_cron.xml',
        'data/phoenix_alarm_data.xml',
        'data/socket_server_data.xml',
        'security/ir.model.access.csv',
        'views/phoenix_audible_address_views.xml',
        'views/socket_server_views.xml',
        'views/phoenix_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_phoenix_alarm/static/src/css/custom_kanban_styles.css',
        ],
    },
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
