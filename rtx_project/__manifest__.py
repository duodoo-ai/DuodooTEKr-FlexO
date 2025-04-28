# -*- coding: utf-8 -*-

{
    "name": "Project(RTX)",
    # "name": "Project(ZYfire)",
    "version": "18.0.0.1",
    "website": "https://eist.com.cn",
    "author": "RAIN@EIST",
    "category": "Services/Project",
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
        # "views/project_large_screen_templates.xml",
        "views/project_menus.xml",
    ],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_backend": [
            "rtx_project/static/src/components/**/*",
            "rtx_project/static/src/views/**/*",
            "rtx_project/static/src/large_screen/**/*",
        ],
        # 大屏的静态资源
        # "rtx_project.assets_largescreen": [
        #     # 1 Define rtx_project variables (takes priority over frontend ones)
        #     "rtx_project/static/src/primary_variables.scss",
        #     "rtx_project/static/src/bootstrap_overridden.scss",
        #     # 2 Load frontend variables
        #     ("include", "web._assets_helpers"),
        #     ("include", "web._assets_frontend_helpers"),
        #     ("include", "web._assets_primary_variables"),
        #     "web/static/src/scss/pre_variables.scss",
        #     # 3 Load Bootstrap and frontend bundles
        #     "web/static/lib/bootstrap/dist/css/bootstrap.css",
        #     "web/static/lib/bootstrap/scss/_functions.scss",
        #     "web/static/lib/bootstrap/scss/_variables.scss",
        #     "web/static/lib/bootstrap/scss/_variables-dark.scss",
        #     "web/static/lib/bootstrap/scss/_maps.scss",
        #     ("include", "web._assets_bootstrap_frontend"),
        #     # 4 large_screen's specific assets
        #     "rtx_project/static/src/large_screen/**/*",
        #     "rtx_project/static/src/components/**/*",
        #     "eist_erp_base/static/libs/bootstrap-icons/font/bootstrap-icons.min.css",
        # ],
    },
    "license": "Other proprietary",
    "post_init_hook": "_rtx_project_post_init",  # 安装后执行的方法
    "uninstall_hook": "_rtx_project_uninstall_hook",  # 卸载后执行的方法
}
