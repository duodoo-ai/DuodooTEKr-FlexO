# -*- coding: utf-8 -*-

{
    "name": "Odoo Extend Project(RTX)",
    # "name": "Project(ZYfire)",
    "version": "18.0.0.1",
    "website": "https://eist.com.cn",
    "author": "RAIN@EIST",
    'category': 'Internet of Things (IoT)',
    "sequence": 45,
    "summary": "Organize and plan your projects",
    "depends": [
        "project",
        "maintenance",
        "web_route_map",
        "eist_web_theme",
        "esit_geolocalize",
        "odoo_maintenance",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "data/project_project_stage_data.xml",
        "data/project_task_type_data.xml",
        "demo/project_xj_demo.xml",
        "demo/project_map_location_xj_1.xml",
        "demo/project_map_location_xj_2.xml",
        "demo/project_map_location_xj_3.xml",
        "demo/project_map_location_xj_4.xml",
        "demo/project_map_location_xj_5.xml",
        "demo/project_map_location_xj_6.xml",
        "demo/project_map_location_xj_7.xml",
        "demo/project_map_location_xj_8.xml",
        "views/res_config_settings_views.xml",
        "views/maintenance.xml",
        "views/project_project_views.xml",
        "views/project_project_stage_views.xml",
        "views/project_map_location_views.xml",
        "views/project_menus.xml",
    ],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_backend": [
            "odoo_project/static/src/components/**/*",
            "odoo_project/static/src/views/**/*",
            "odoo_project/static/src/large_screen/**/*",
        ],
    },
    "license": "Other proprietary",
    "post_init_hook": "_odoo_project_post_init",  # 安装后执行的方法
    "uninstall_hook": "_odoo_project_uninstall_hook",  # 卸载后执行的方法
}
