# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    # 获取项目时间运行天数
    @api.model
    def get_project_running_time(self):
        """
        获取最早启用项目时间(`pipeline_activation_time`)的记录,获取记录的字段`running_stage_id` 的值
        return:
            若没有记录, 则返回0天
            若有记录, 则返回记录的字段`duration_tracking` 的值(字典类型)
        """
        running_stage_id = (
            self.env["project.project.stage"].sudo().search([("code", "=", "running")], limit=1)
        ).id
        earliest_project = self.env["project.project"].search(
            [("stage_id", "=", running_stage_id)], order="pipeline_activation_time ASC", limit=1
        )

        if earliest_project:
            # 使用 get 方法安全地获取字典值，如果键不存在则返回 "0"
            running_time = earliest_project.duration_tracking.get(str(running_stage_id), "0")
            return running_time
        else:
            return "0"
