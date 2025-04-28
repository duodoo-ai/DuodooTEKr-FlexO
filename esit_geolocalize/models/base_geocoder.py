# -*- coding: utf-8 -*-

import requests
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class GeoProvider(models.Model):
    _inherit = "base.geo_provider"

    tech_name = fields.Char(string="Technical Name", translate=False)
    name = fields.Char(translate=True)


class GeoCoder(models.AbstractModel):
    _inherit = "base.geocoder"

    @api.model
    def get_provider_info(self):
        data = {
            "has_error": False,
        }
        ICP = self.env["ir.config_parameter"].sudo()
        prov_id = ICP.get_param("base_geolocalize.geo_provider")

        if prov_id:
            provider = self.env["base.geo_provider"].browse(int(prov_id))
            data.update({"has_error": False, "name": provider.name})
        else:
            data.update(
                {
                    "has_error": True,
                    "message": _("The geo provider is not configured!"),
                    "suggtions": _("Please contact your administrator to configure the geo provider!"),
                }
            )
            return data

        geo_provider_name = provider.tech_name.split("_map_")[0]
        # print(geo_provider_name)
        geo_provider_key = ICP.search(
            [("key", "=like", f"base_geolocalize.{geo_provider_name}%")], limit=None
        )
        # print(geo_provider_key)
        if not geo_provider_key:
            data.update(
                {
                    "has_error": True,
                    "message": _("The key for GEO provider '%s' is not configured!" % provider.name),
                    "suggtions": _(
                        "Please contact your administrator to configure the key for the geographic information provider!"
                    ),
                }
            )
            return data
        else:
            key = ""
            if geo_provider_name == "amap":
                geo_provider_key = ICP.search(
                    [("key", "=like", "base_geolocalize.amap_map_jsapi_key")], limit=1
                )
                key = geo_provider_key.value
            else:
                key = geo_provider_key.value

            data.update({"has_error": False, "tech_name": provider.tech_name, "key": key})

        return data

    @api.model
    def get_provider_tech_name(self):
        prov_id = self.env["ir.config_parameter"].sudo().get_param("base_geolocalize.geo_provider")
        if prov_id:
            provider = self.env["base.geo_provider"].browse(int(prov_id))
        if not prov_id or not provider.exists():
            provider = self.env["base.geo_provider"].search([], limit=1)
        return provider.tech_name

    @api.model
    def _call_tencentmap(self, addr, **kw):
        """
        使用腾讯地图的 API。如果没有有效的 API 密钥，它将无法工作。
        :return: （纬度、经度）或 None（如果未找到）
        """
        apikey = self.env["ir.config_parameter"].sudo().get_param("base_geolocalize.tencent_map_api_key")
        if not apikey:
            raise UserError(
                _(
                    "Tencent Location Service API key is required..\n"
                    "Visit https://lbs.qq.com/faq/accountQuota/faqKey for more information."
                )
            )
        # 腾讯位置服务的地理编码 API URL
        url = "https://apis.map.qq.com/ws/geocoder/v1/"

        # 构建请求参数
        params = {"address": addr, "key": apikey}

        # 发送 GET 请求
        try:
            result = requests.get(url, params=params).json()
        except Exception as e:
            self._raise_query_error(e)

        # 解析响应
        try:
            if result["status"] != 0:
                error_msg = result["message"]
                raise UserError(error_msg)
            geo = result["result"]["location"]
            return float(geo["lat"]), float(geo["lng"])
        except (KeyError, ValueError):
            _logger.debug(
                "Unexpected Tencent Location Service API answer %s", result.get("error_message", "")
            )
            return None

    @api.model
    def _geo_query_address_tencentmap(self, street=None, zip=None, city=None, state=None, country=None):
        address = self._geo_query_address_default(
            street=street, zip=zip, city=city, state=state, country=country
        )
        # 使用split()方法将地址字符串分割成列表
        address_list = address.split(", ")

        # 使用切片操作将列表倒序
        reversed_address_list = address_list[::-1]

        # 使用join()方法将列表重新组合成字符串
        reversed_address = ", ".join(reversed_address_list)
        return reversed_address.replace(",", "")

    @api.model
    def _call_amap(self, addr, **kw):
        """
        使用高德地图的 API。如果没有有效的 API 密钥，它将无法工作。
        :return: （纬度、经度）或 None（如果未找到）
        """
        apikey = self.env["ir.config_parameter"].sudo().get_param("base_geolocalize.amap_map_api_key")
        if not apikey:
            raise UserError(
                _(
                    "AMap Open Platform API key is required..\n"
                    "Visit https://lbs.amap.com/faq/quota-key/key/ for more information."
                )
            )

        # 高德地图开放平台的地理编码 API URL
        url = "https://restapi.amap.com/v3/geocode/geo"
        # 处理地址字符串， 'address': '武汉地铁1号线径河站, 武汉市, 湖北省
        # 使用split()方法将地址字符串分割成列表
        address_list = addr.split(", ")

        # 使用切片操作将列表倒序
        reversed_address_list = address_list[::-1]

        # 使用join()方法将列表重新组合成字符串
        reversed_address = ", ".join(reversed_address_list)

        # 构建请求参数
        params = {"address": reversed_address.replace(",", ""), "key": apikey}
        # 发送 GET 请求
        try:
            result = requests.get(url, params=params).json()
        except Exception as e:
            self._raise_query_error(e)

        # 解析响应
        try:
            if result["status"] != 1:
                error_msg = result["info"]
                raise UserError(error_msg)
            geo = result["result"]["geocodes"]["location"]
            return float(geo[1]), float(geo[0])
        except (KeyError, ValueError):
            _logger.debug("Unexpected AMap Open Platform API answer %s", result.get("error_message", ""))
            return None

    # ---------------------------------------------
    # 在地图上定位
    # ---------------------------------------------
    @api.model
    def geo_localize_on_map(self, addr, city, resModel, resId, resFields, **kw):
        """
        使用位置提供程序 API 弹窗供用户选择地址，以转换为坐标。
        :param addr:传递给 API 的地址字符串
        :return: （纬度、经度）或 None（如果未找到）
        """
        provider = self._get_provider().tech_name
        # api_url, lib_url, service_url, key = self.get_geo_provider_info(provider)
        api_url, key = self.get_geo_provider_info(provider)
        if provider == "tencentmap":
            action = {
                "type": "ir.actions.client",
                "tag": "display_tencent_map_dialog",
                "params": {
                    "api_url": api_url,
                    "key": key,
                    "address": addr,
                    "city": city,
                    "resModel": resModel,
                    "resId": resId,
                    "resFields": resFields,
                    # "city": kw.get("city"),
                    # "resModel": kw.get("res_model"),
                    # "resId": kw.get("res_id"),
                },
            }
        return action

    def get_geo_provider_info(self, tech_name):
        # tech_name = self._get_provider().tech_name
        ICP = self.env["ir.config_parameter"].sudo()
        geo_provider_name = tech_name.split("map")[0]
        geo_provider_key = ICP.search(
            [("key", "=like", f"base_geolocalize.{geo_provider_name}%")], limit=None
        )

        if tech_name == "tencentmap":
            api_url = "https://map.qq.com/api/gljs?v=1.exp&libraries=service,geocoder,drawing,geometry,autocomplete,convertor"
        if tech_name == "amap":
            api_url = "https://restapi.amap.com/v5/place/text?parameters"

        return api_url, geo_provider_key.value

    # ---------------------------------------------
    # 在地图上计算距离
    # ---------------------------------------------
    @api.model
    def geo_compute_straight_line_distance(self, start, end, **kw):
        """
        计算2个坐标点之间的直线距离(单位：米)
        :param paths: 坐标路径元组，每个路径是一个包含两个元素的元组，分别是纬度和经度
        :return: 距离（单位：米）
        """
        provider = self._get_provider().tech_name
        try:
            service = getattr(self, "_geo_compute_straight_line_distance_" + provider)
            result = service(start, end, **kw)
        except AttributeError:
            raise UserError(_("Provider %s is not implemented for geolocation service.", provider))
        except UserError:
            raise
        except Exception:
            _logger.debug("Geolocalize call failed", exc_info=True)
            result = None
        return result

    @api.model
    def _geo_compute_straight_line_distance_tencentmap(self, start, end):
        """
        计算两个坐标点之间的直线距离(单位：米)
        文档: https://lbs.qq.com/service/webService/webServiceGuide/route/webServiceMatrix
        :param start: 起点坐标字符串 "latitude, longitude"
        :param end: 终点坐标字符串 "latitude, longitude"
        :return: 直线距离（单位：千米）
        """
        print(start, end)
        apikey = self.env["ir.config_parameter"].sudo().get_param("base_geolocalize.tencent_map_api_key")
        if not apikey:
            raise UserError(_("The Tencent Map API key is not configured"))

        url = "https://apis.map.qq.com/ws/distance/v1/"  # 腾讯位置服务的直线距离计算 API URL
        params = {
            "key": apikey,
            "mode": "straight",  # 可选值：‘driving’驾车,‘walking’步,默认：'walking’,‘straight’直线
            "from": start,
            "to": end,
        }
        print(params)

        try:
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            print(result)

            if result["status"] != 0:
                _logger.error("腾讯位置服务API错误: %s", result.get("message"))
                return 0.0

            # 解析直线距离结果
            if result.get("result", {}).get("elements"):
                return result["result"]["elements"][0]["distance"]

            return 0.0

        except requests.exceptions.Timeout:
            _logger.error("腾讯位置服务API请求超时")
            return 0.0
        except Exception as e:
            _logger.exception("地理位置直线距离计算异常: %s", str(e))
            return 0.0
