# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _

ONLINE_SYNC_PIPELINE_FIELDS = [
    "pipeline_no",
    "pipeline_activation_time",
    "pipeline_length",
    "monthly_traffic",
    "seasonal_traffic",
    "year_traffic",
    "real_input_traffic",
    "real_output_traffic",
    "total_traffic",
]


class Project(models.Model):
    _inherit = "project.project"

    locations = fields.One2many("project.map.location", "project_id", string="Project Locations")

    # 管道
    pipeline_node_has_exception = fields.Boolean(string="Pipeline node has exception", default=False, compute="_compute_pipeline_node_has_exception")
    pipeline_no = fields.Char(string="Pipeline No.")
    pipeline_activation_time = fields.Datetime(
        string="Pipeline activation time",
        readonly=True,
        store=True,
        compute="_compute_pipeline_activation_time",
    )
    pipeline_diameter = fields.Float(
        string="Pipeline diameter", digits=(10, 0), store=True, default=0
    )  # 管道口径

    pipeline_length = fields.Float(
        string="Length(km)", digits=(10, 2), readonly=True, store=True, default=0.00
    )  # 项目长度 (总长度 10 位, 小数保留 2 位)

    # 流量
    monthly_traffic = fields.Float(
        string="Monthly traffic", digits=(10, 2), default=0.00, readonly=True
    )  #  当月流量 (总长度10位，小数保留2位)
    seasonal_traffic = fields.Float(
        string="Seasonal traffic", digits=(10, 2), default=0.00, readonly=True
    )  # 当季流量 (总长度10位，小数保留2位)
    year_traffic = fields.Float(
        string="Year traffic", digits=(10, 2), default=0.00, readonly=True
    )  # 当年流量 (总长度10位，小数保留2位)
    real_input_traffic = fields.Float(
        string="Real Input traffic", digits=(10, 2), default=0.00, readonly=True
    )  # 实时输入流量 (总长度10位，小数保留2位)
    real_output_traffic = fields.Float(
        string="Real Output traffic", digits="(10, 2)", default=0.00, readonly=True
    )  # 实时输出流量 (总长度10位，小数保留2位)
    total_traffic = fields.Float(
        string="Total traffic", digits=(10, 2), readonly=True, store=True, default=0.00
    )  #  总供水量 (总长度10位，小数保留2位)

    # --------------------------
    # onchange
    # --------------------------

    # --------------------------
    # 计算 locations
    # --------------------------

    @api.depends("locations")
    def _compute_pipeline_node_has_exception(self):
        """
        计算项目下是否有异常节点
        """
        for project in self:
            node_has_exception_count = project.locations.search_count(
                [
                    ("project_id", "=", project.id),
                    ("status", "!=", "normal"),
                ]
            )
            if node_has_exception_count > 0:
                project.pipeline_node_has_exception = True
            else:
                project.pipeline_node_has_exception = False


    @api.depends("stage_id")
    def _compute_pipeline_activation_time(self):
        """
        计算管线第一次启用的时间
        """
        for project in self:
            if project.stage_id.code == "running" and not project.pipeline_activation_time:
                project.pipeline_activation_time = fields.Datetime.now()

    # --------------------------
    # ORM
    # --------------------------
    def write(self, vals):
        """
        监听项目更新的值，通过 bus 通知 前端更新
        """
        res = super(Project, self).write(vals) if vals else True
        try:
            if self.id:
                project = self.env["project.project"].browse(self.id)
                projects = self.env["project.project"].sudo().search([("locations", "!=", False)])
                sync_data = {key: val for key, val in vals.items() if key in ONLINE_SYNC_PIPELINE_FIELDS}
                if sync_data:
                    sync_data.update(
                        {
                            "duration_tracking": project.duration_tracking,
                        }
                    )

                    # 发送项目概况数据
                    self.env.ref("project.group_project_user").users._bus_send(
                        "online_sync_pipeline",
                        {
                            "id": project.id,
                            "sync_data": sync_data,
                        },
                    )

                    dashboard_data = {
                        "total_pipeline_qty": len(projects),
                        "running_pipeline_qty": self.env["project.project"]
                        .sudo()
                        .search_count(
                            [
                                (
                                    "stage_id",
                                    "=",
                                    self.env["ir.model.data"]._xmlid_to_res_id(
                                        "odoo_project.project_project_stage_running"
                                    ),
                                )
                            ]
                        ),
                        "stopped_pipeline_qty": self.env["project.project"]
                        .sudo()
                        .search_count(
                            [
                                (
                                    "stage_id",
                                    "=",
                                    self.env["ir.model.data"]._xmlid_to_res_id(
                                        "odoo_project.project_project_stage_stopped"
                                    ),
                                )
                            ]
                        ),
                        # "total_traffic": sum(projects.mapped("total_traffic")),
                        "total_traffic": sum(item['total_traffic'] for item in projects),
                        "monthly_traffic": sum(item['monthly_traffic'] for item in projects),
                        "seasonal_traffic": sum(item['seasonal_traffic'] for item in projects),
                        "year_traffic": sum(item['year_traffic'] for item in projects),
                    }
                    # print("发送仪表板数据数据-------------", dashboard_data)
                    # 发送仪表板数据
                    self.env.ref("project.group_project_user").users._bus_send(
                        "online_sync_pipeline_dashboard_data",
                        {
                            "dashboard_data": dashboard_data,
                        },
                    )
        except Exception as e:
            pass

        return res

    def get_locations_by_project_ids(self):
        """
        根据项目 id 获取项目的坐标集合
        """
        project_list = []

        if len(self.ids) > 0:
            projects = self.env["project.project"].search(
                [("id", "in", self.ids), ("locations", "!=", False)]
            )
        else:
            projects = self.env["project.project"].search([("locations", "!=", False)])

        timezone = self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        self_tz = self.with_context(tz=timezone)

        running_stage_id = (
            self.env["project.project.stage"].sudo().search([("code", "=", "running")], limit=1)
        ).id
        for project in projects:
            locations = []
            if project.locations:
                project_obj = {
                    "id": project.id,
                    "name": project.name,
                    "partner_name": project.partner_id.name if project.partner_id else "",
                    "pipeline_no": project.pipeline_no,  # 管线号
                    "pipeline_activation_time": fields.Datetime.context_timestamp(
                        self_tz, project.pipeline_activation_time
                    ).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),  # 管线第一次启用时间
                    # "pipeline_running_time": fields.Datetime.context_timestamp(
                    #     self_tz, project.pipeline_running_time
                    # ).strftime(
                    #     "%Y-%m-%d %H:%M:%S"
                    # ),  # 管线运行时间
                    "running_stage_id": running_stage_id,
                    "stage": project.stage_id.code,
                    "duration_tracking": project.duration_tracking, # 管道运行时间
                    "pipeline_length": project.pipeline_length,
                    "monthly_traffic": project.monthly_traffic,
                    "seasonal_traffic": project.seasonal_traffic,
                    "year_traffic": project.year_traffic,
                    "real_input_traffic": project.real_input_traffic,
                    "real_output_traffic": project.real_output_traffic,
                    "pipeline_diameter": project.pipeline_diameter,  # 管线直径
                    "total_traffic": project.total_traffic,
                    "last_update_status": project.last_update_status,
                }
                for location in project.locations:
                    locations.append(
                        {
                            "sequence": location.sequence,
                            "id": location.id,
                            "name": location.name,
                            "description": location.description,
                            "country": location.country_id.name,
                            "city": location.city,
                            "state": location.state_id.name,
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "length": location.length,
                            "real_input_traffic": location.real_input_traffic,
                            "real_output_traffic": location.real_output_traffic,
                            "status": location.status,
                        }
                    )
                project_obj.update({"locations": locations})
            project_list.append(project_obj)
        # print(project_list)
        return project_list

    @api.model
    def set_project_length(self, project_id, project_length):
        """
        设置项目长度
        """
        pipeline_length = self.browse(project_id).pipeline_length
        if pipeline_length != project_length:
            self.browse(project_id).pipeline_length = project_length
