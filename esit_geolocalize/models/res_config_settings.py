# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    geoloc_provider_tencentmap_key = fields.Char(
        string="Tencent Map API Key",
        config_parameter="base_geolocalize.tencent_map_api_key",
        help="Visit https://lbs.qq.com/dev/console/home for more information.",
    )
    geoloc_provider_amap_jsapi_key = fields.Char(
        string="Amap JSAPI Key",
        config_parameter="base_geolocalize.amap_map_jsapi_key",
        help="Visit https://console.amap.com/dev/id/phone for more information.",
    )  #

    geoloc_provider_amap_webservices_key = fields.Char(
        string="Amap Web Services Key",
        config_parameter="base_geolocalize.amap_map_webservices_key",
        help="Visit https://console.amap.com/dev/id/phone for more information.",
    )  #
