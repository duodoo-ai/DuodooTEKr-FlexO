# -*- coding: utf-8 -*-

from __future__ import annotations

from odoo import api, fields, models, _
from odoo.tools import config

import typing

if typing.TYPE_CHECKING:
    from .res_country import Country, CountryState

ONLINE_SYNC_PIPELINE_NODE_FIELDS = [
    "description",
    "real_input_traffic",
    "real_output_traffic",
    # "length",
    "status",
]


class ProjectMapLocation(models.Model):
    _name = "project.map.location"
    _inherit = ["mail.thread"]
    _description = "Project map location"

    @api.model
    def _default_company_id(self):
        if self._context.get("default_project_id"):
            return self.env["project.project"].browse(self._context["default_project_id"]).company_id
        return False

    def name_get(self):
        result = []
        for record in self:
            print(record.project_id)
            if record.project_id:
                name = f"{record.project_id.name}_{record.name}"
            else:
                name = record.name
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
        if args is None:
            args = []
        domain = args + ["|", ("name", operator, name), ("project_id.name", operator, name)]
        return self._search(domain, limit=limit, access_rights_uid=name_get_uid)

    name = fields.Char(string="Name", required=True, index="trigram")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        compute="_compute_company_id",
        store=True,
        readonly=False,
        recursive=True,
        copy=True,
        default=_default_company_id,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        domain="['|', ('company_id', '=', False), ('company_id', '=?',  company_id)]",
        # precompute=True,
        recursive=True,
        readonly=False,
        index=True,
        change_default=True,
    )

    equipment_ids = fields.One2many(
        "maintenance.equipment",
        "location_id",
        string="Maintenance Equipment",
        # 自动反向更新 location_id
        auto_join=True,
    )

    api.depends("project_id", "name")

    def _compute_display_name(self):
        for record in self:
            if record.project_id:
                record.display_name = f"{record.project_id.name}_{record.name}"
            else:
                record.display_name = record.name

    display_name = fields.Char(compute="_compute_display_name", store=True)

    stage_id = fields.Many2one("project.project.stage", related="project_id.stage_id")

    description = fields.Html(string="Description", sanitize_attributes=False)
    sequence = fields.Integer(string="Sequence", default=1, export_string_translation=False)
    active = fields.Boolean(default=True, export_string_translation=False)

    street = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id: CountryState = fields.Many2one(
        "res.country.state", string="State", ondelete="restrict", domain="[('country_id', '=?', country_id)]"
    )
    country_id: Country = fields.Many2one("res.country", string="Country", ondelete="restrict")
    country_code = fields.Char(related="country_id.code", string="Country Code")

    date_localization = fields.Date(string="Geolocation Date")
    latitude = fields.Float(string="Geo Latitude", digits=(10, 7))  # 纬度
    longitude = fields.Float(string="Geo Longitude", digits=(10, 7))  # 经度

    imei = fields.Char(string="IMEI")  # 序列号 (IMEI)，设备唯一标识码
    real_input_traffic = fields.Float(
        string="Real Input traffic", digits=(10, 2), default=0.00, readonly=True
    )  # 实时输入流量 (总长度 10 位，小数保留 2 位)
    real_output_traffic = fields.Float(
        string="Real Output traffic", digits=(10, 2), default=0.00, readonly=True
    )  # 实时输出流量 (总长度 10 位，小数保留 2 位)

    distance = fields.Float(
        string="Distance(km)",
        digits=(10, 2),
        readonly=True,
        store=True,
        default=0.00,
        help="Distance from the previous location",
    )  #  与上一个节点的距离 (总长度 10 位，小数保留 2 位)
    length = fields.Float(
        string="Length(km)",
        digits=(10, 2),
        readonly=True,
        store=True,
        default=0.00,
        help="Total length, Distance from the starting location",
    )  #  与起始节点的距离 (总长度 10 位，小数保留 2 位)

    status = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("exception", "Exception"),
        ],
        string="Status",
        default="normal",
    )

    # --------------------------
    # onchange
    # --------------------------
    @api.onchange("status")
    def _onchange_status(self):
        if self.status == "exception":
            self.project_id.pipeline_node_has_exception = True
        else:
            for location in self.project_id.locations:
                if location.status == "exception":
                    self.project_id.pipeline_node_has_exception = True
                    break
                else:
                    self.project_id.pipeline_node_has_exception = False

    # --------------------------
    # 计算
    # --------------------------
    @api.depends("project_id.company_id")
    def _compute_company_id(self):
        for location in self:
            if not not location.project_id:
                continue
            location.company_id = location.project_id.company_id

    # --------------------------
    # ORM
    # --------------------------
    def write(self, vals):
        """
        监听地图位置更新的值，通过 bus 通知 前端更新 ProjectMapLocation
        """
        res = super(ProjectMapLocation, self).write(vals) if vals else True
        try:
            if self.id:
                node_data = {key: val for key, val in vals.items() if key in ONLINE_SYNC_PIPELINE_NODE_FIELDS}
                node = self.env["project.map.location"].browse(self.id)
                if node_data:
                    # print("节点更新的数据",node_data)
                    # 发送节点数据
                    self.env.ref("project.group_project_user").users._bus_send(
                        "online_sync_pipeline_node",
                        {
                            "project_id": node.project_id.id,
                            "location_id": node.id,
                            "node_data": node_data,
                        },
                    )

        except Exception as e:
            pass

        return res

    def geo_localize_on_map(self):
        """
        在地图上定位
        """
        geo_obj = self.env["base.geocoder"]
        search = geo_obj.geo_query_address(
            street=self.street,
            zip=self.zip,
            city=self.city,
            state=self.state_id.name,
            country=self.country_id.name,
        )
        return geo_obj.geo_localize_on_map(
            search, self.city, "project.map.location", self.id, ["latitude", "longitude"]
        )

    @api.model
    def set_project_location_length(self, location_id, location_length):
        """
        设置项目位置长度
        """
        length = self.browse(location_id).length
        if length != location_length:
            self.browse(location_id).length = location_length

    @api.model
    def _geo_localize(self, street="", zip="", city="", state="", country=""):
        geo_obj = self.env["base.geocoder"]
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    def project_geo_distance(self):
        """
        计算距离
        """
        geo_obj = self.env["base.geocoder"]

        for location in self:
            previous_location = self.env["project.map.location"].search(
                [("project_id", "=", location.project_id.id), ("sequence", "<", location.sequence)], limit=1
            )
            paths = []
            if not previous_location:
                self.write({"distance": 0.00, "length": 0.00})
            else:
                start_location = f"{previous_location.latitude},{previous_location.longitude}"
                end_location = f"{location.latitude},{location.longitude}"
                print(start_location)
                print(end_location)
                # 计算距离
                distance = geo_obj.geo_compute_straight_line_distance(start_location, end_location)
                print(distance)

    def geo_localize(self):
        # We need country names in English below
        if not self._context.get("force_geo_localize") and (
            self._context.get("import_file")
            or any(config[key] for key in ["test_enable", "test_file", "init", "update"])
        ):
            return False
        location_not_geo_localized = self.env["project.map.location"]
        for location in self.with_context(lang="en_US"):
            result = self._geo_localize(
                location.street,
                location.zip,
                location.city,
                location.state_id.name,
                location.country_id.name,
            )

            if result:
                location.write(
                    {
                        "latitude": result[0],
                        "longitude": result[1],
                        "date_localization": fields.Date.context_today(location),
                    }
                )
            else:
                location_not_geo_localized |= location
        if location_not_geo_localized:
            self.env.user._bus_send(
                "simple_notification",
                {
                    "type": "danger",
                    "title": _("Warning"),
                    "message": _(
                        "No match found for %(names)s address(es).",
                        names=", ".join(location_not_geo_localized.mapped("name")),
                    ),
                },
            )
        return True


