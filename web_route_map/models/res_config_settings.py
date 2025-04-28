# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    map_provider = fields.Selection(
        string="Default Map Provider",
        selection=[("amap", "Amap"), ("tencent_map", "Tencent Map"), ("map_box", "MapBox")],
        default="amap",
        config_parameter="web_map.map_provider",
        help="Default map provider to use",
        copy=False,
    )

    # 高德地图
    amap_jsapi_key = fields.Char(
        string="Amap JSAPI Key",
        config_parameter="web_map.amap_jsapi_key",
        help="Necessary for some functionalities in the map view",
        copy=False,
        default="",
        store=True,
    )
    amap_web_services_key = fields.Char(
        string="Amap Web Services Key",
        config_parameter="web_map.amap_web_service_key",
        help="Necessary for some functionalities in the map view",
        copy=False,
        default="",
        store=True,
    )
    amap_map_style = fields.Selection(
        [
            ("normal", "Normal"), # 标准
            ("dark", "Phantom Black"), # 幻影黑
            ("light", "Moonshine silver"), # 月光银
            ("whitesmoke", "Far Mountains"), # 远山黛
            ("fresh", "The grass is blue"), # 草色青
            ("grey", "Ascot Grey"), # 雅士灰
            ("graffiti", "Graffiti"), # 涂鸦
            ("macaron", "Macaron"), # 马卡龙
            ("blue", "Indigo blue"), # 靛青蓝
            ("darkblue", "Polar Night Blue"), # 极夜蓝
            ("wine", "Sauce seed"), # 酱籽
        ],
        string="Amap map style",
        config_parameter="web_map.amap_map_style",
        help="Go to Create a custom map style: https://lbs.amap.com/dev/mapstyle/index",
        copy=False,
        default="normal",
        store=True,
    )  # https://lbs.amap.com/dev/mapstyle/index b

    # 腾讯地图
    tencent_map_key = fields.Char(
        string="Tencent Map Key",
        config_parameter="web_map.tencent_map_key",
        help="Necessary for some functionalities in the map view",
        copy=False,
        default="",
        store=True,
    )

    # MapBox
    map_box_token = fields.Char(
        config_parameter="web_map.token_map_box",
        string="Token Map Box",
        help="Necessary for some functionalities in the map view",
        copy=False,
        default="",
        store=True,
    )

    @api.model
    def get_emap_provider_info(self):
        """
        获取地图提供商的信息
        """
        data = {
            "has_error": False,
        }
        ICP = self.env["ir.config_parameter"].sudo()
        map_provider = ICP.get_param("web_map.map_provider")

        if map_provider == "amap":
            data.update(
                {
                    "tech_name": "amap",
                    "invalid_provider": True,
                }
            )
            amap_jsapi_key = ICP.get_param("web_map.amap_jsapi_key")
            if not amap_jsapi_key:
                data.update(
                    {
                        "has_error": True,
                        "not_configured": False,
                        "message": _("Amap JSAPI Key is not configured"),
                        "suggtions": _("Please contact your administrator to configure the E-map provider!"),
                    }
                )
            else:
                data.update(
                    {
                        "has_error": False,
                        "key": amap_jsapi_key,
                    }
                )
        elif map_provider == "tencent_map":
            data.update(
                {
                    "tech_name": "tencent_map",
                    "invalid_provider": True,
                }
            )
            tencent_map_key = ICP.get_param("web_map.tencent_map_key")
            if not tencent_map_key:
                data.update(
                    {
                        "has_error": True,
                        "not_configured": False,
                        "message": _("Tencent Map Key is not configured"),
                        "suggtions": _("Please contact your administrator to configure the E-map provider!"),
                    }
                )
            else:
                data.update(
                    {
                        "has_error": False,
                        "key": tencent_map_key,
                    }
                )
        elif map_provider == "map_box":
            data.update(
                {
                    "tech_name": "map_box",
                    "invalid_provider": True,
                }
            )
            map_box_token = ICP.get_param("web_map.token_map_box")
            if not map_box_token:
                data.update(
                    {
                        "has_error": True,
                        "not_configured": False,
                        "message": _("Map Box Token is not configured"),
                        "suggtions": _("Please contact your administrator to configure the E-map provider!"),
                    }
                )
            else:
                data.update(
                    {
                        "has_error": False,
                        "key": map_box_token,
                    }
                )
        else:
            data.update(
                {
                    "has_error": True,
                    "invalid_provider": True,
                    "message": _("Invalid map provider"),
                }
            )

        return data
