# -*- coding: utf-8 -*-
{
    'name': "Odoo Extend Maintenance(RTX)",

    'summary': """
    Track equipment and maintenance requests
    """,

    'description': """Track equipment and manage maintenance requests
                    More Support：
                    18951631470
                    zou.jason@qq.com
                    """,

    'author': "Jason Zou",
    "website": "-",

    'category': 'Internet of Things (IoT)',
    'version': '1.0',

    'depends': ['base', 'mail', 'web', 'maintenance', 'project'],
    'external_dependencies': {
            'python': ['qrcode', 'PIL'],
        },
    'data': [
        'data/maintenance_data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'report/qrcode_report_templates.xml',  # 添加报告文件

        'views/maintenance_category_views.xml',
        'views/maintenance_request.xml',
        'views/maintenance_monitor_fluid_views.xml',  # 流体监控
        'views/maintenance_spec_views.xml',    # 设备监控数据
        'views/maintenance_spec_inherit_views.xml',    # 技术指标
        # 'views/maintenance_monitor_data_views.xml',  # 监控指标字段扩展
        'views/maintenance_monitor_fluid_views.xml',  # 流体监控
        # 'views/maintenance_inspection_views.xml',  # 设备巡检记录
        'views/maintenance.xml',
        'views/menu_views.xml',
        'views/menu_hide_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_maintenance/static/src/js/qrcode_report.js',
            'odoo_maintenance/static/src/css/qrcode_style.css',
            'odoo_maintenance/static/src/js/instascan.min.js',
            'odoo_maintenance/static/src/css/qr_scanner.css',
            # 'odoo_maintenance/static/src/js/qr_scanner.js',
            'odoo_maintenance/static/src/xml/qr_template.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
