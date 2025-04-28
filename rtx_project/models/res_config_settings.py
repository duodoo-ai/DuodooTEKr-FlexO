# -*- coding: utf-8 -*-


from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 供水项目设置
    water_supply_pipeline_normal_state_color = fields.Char(
        string="Normal state color of water supply pipeline",
        config_parameter="water_supply_pipeline.normal_state_color",
        default="#a3cfbb",
    )
    water_supply_pipeline_exception_state_color = fields.Char(
        string="Color of abnormal state of water supply pipeline",
        config_parameter="water_supply_pipeline.exception_state_color",
        default="#fff3cd",
    )

    # 供水项目 大屏幕设置
    water_supply_pipeline_large_screen_title = fields.Char(
        string="Monitor the background color of the large screen",
        config_parameter="water_supply_pipeline.large_screen_title",
        default=_("Smart water supply operation system"),
        translate=True,
    )
    water_supply_pipeline_large_screen_background_color = fields.Char(
        string="Monitor the background color of the large screen",
        config_parameter="water_supply_pipeline.large_screen_background_color",
        default="#004b7a",
    )
