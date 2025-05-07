# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ------------------------------------------------------------
    # 品牌设置
    # ------------------------------------------------------------
    system_name = fields.Char(
        string="System Name",
        readonly=False,
        default="EIST ERP",
        config_parameter="eist_erp.system_name",
    )
    display_company_name = fields.Boolean(
        string="Display Company Name",
        default=False,
        config_parameter="eist_erp.display_company_name",
    )
    # full_system_name = fields.Char(
    #     config_parameter="eist_erp.full_system_name", compute="_compute_full_system_name"
    # )
    logo = fields.Binary(related="company_id.logo", readonly=False)
    square_logo = fields.Binary(related="company_id.square_logo", readonly=False)
    favicon = fields.Binary(related="company_id.favicon", readonly=False)
    copyright = fields.Char(related="company_id.copyright", readonly=False)
    doc_url = fields.Char(related="company_id.doc_url", readonly=False)
    support_url = fields.Char(related="company_id.support_url", readonly=False)

    # 应用
    module_eist_web_theme = fields.Boolean(string="Web Theme", default=False)
    module_eist_web_toolbox = fields.Boolean(string="Web ToolBox", default=False)
    module_eist_report_management = fields.Boolean(string="Report Management", default=False)

    hide_enterprise_app = fields.Boolean(
        string="Hide Enterprise App",
        default=False,
        config_parameter="eist_erp.hide_enterprise_app",
    )

    # 解决方案-Pos
    module_eist_pos = fields.Boolean(string="Solutions for stores and restaurants", default=False)

    # 解决方案-社交应用
    module_eist_social_app = fields.Boolean(string="Integrate social app solutions", default=False)
    module_eist_social_wechat = fields.Boolean(string="WeChat integration", default=False)
    module_eist_social_wecom = fields.Boolean(string="Wecom integration", default=False)
    module_eist_social_feishu = fields.Boolean(string="Feishu integration", default=False)
    module_eist_social_dingding = fields.Boolean(string="Dingding integration", default=False)

    # 扩展功能
    module_esit_geolocalize = fields.Boolean(string="Partners Geolocation", default=False)
    module_eist_multi_platform = fields.Boolean(string="Multi platform access", default=False)

    @api.onchange("hide_enterprise_app")
    def _onchange_hide_enterprise_app(self):
        """
        隐藏企业版应用
        """
        modules = self.env["ir.module.module"].search(
            ["&", ("to_buy", "=", True), ("application", "=", True)]
        )
        for module in modules:
            module.write({"application": not self.hide_enterprise_app})
        self.env["ir.module.module"].update_list()  # 避免打开设置页面报错

    @api.depends("company_id", "system_name", "display_company_name")
    def _compute_full_system_name(self):
        for record in self:
            print("company_id", company_id.name)
            main_company = self.sudo().env.ref("base.main_company")
            if record.display_company_name:
                record.full_system_name = "%s - %s" % (
                    main_company.name,
                    record.system_name,
                )
            else:
                record.full_system_name = record.system_name
