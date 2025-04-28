# -*- coding: utf-8 -*-

{
    "name": "Partners Geolocation(EIST)",
    "version": "18.0.0.1",
    "category": "Extra Tools",
    "description": """
Partners Geolocation
========================
    """,
    "depends": ["base_geolocalize", "eist_web_widgit", "eist_erp_base"],
    "data": [
        # "security/ir.model.access.csv",
        # "views/geo_provider_view.xml",
        # "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "data/geo_provider_data.xml",
    ],
    "auto_install": ["eist_erp_base"],
    "assets": {
        "web.assets_backend": [
            "esit_geolocalize/static/src/webclient/**/*",
        ],
    },
    "external_dependencies": {
        # "python": ["geopy"],
    },
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
