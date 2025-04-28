# -*- coding: utf-8 -*-


from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        if self.env.user._is_internal():
            result.update(
                map_provider = self.env['ir.config_parameter'].sudo().get_param('web_map.map_provider',"amap"),
                amap_jsapi_key = self.env['ir.config_parameter'].sudo().get_param('web_map.amap_jsapi_key',False),
                amap_web_service_key = self.env['ir.config_parameter'].sudo().get_param('web_map.amap_web_service_key',False),
                amap_map_style = self.env['ir.config_parameter'].sudo().get_param('web_map.amap_map_style',False),
                map_box_token = self.env['ir.config_parameter'].sudo().get_param('web_map.map_box_token',False),
                tencent_map_key = self.env['ir.config_parameter'].sudo().get_param('web_map.tencent_map_key',False),
            )
        return result
