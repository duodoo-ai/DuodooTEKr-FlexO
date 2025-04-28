# -*- coding: utf-8 -*-

{
    "name": "Route Map View",
    "summary": "Define the route map view of Odoo",
    "description": "Allows you to view records on the route map",
    "category": "Extra Tools",
    "author": "RStudio",
    "website": "https://eist.com.cn",
    "version": "18.0.0.1",
    "depends": ["web", "base_setup"],
    "excludes": [
        "web_map",
    ],
    "data": [
        "data/ir_config_parameter_data.xml",
        "views/res_config_settings.xml",
        "views/res_partner_views.xml",
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend_lazy": [
            "web_route_map/static/src/views/**/*",
        ],
        "web.assets_backend": [
            "web_route_map/static/src/utils/**/*",
        ],
    },
}
