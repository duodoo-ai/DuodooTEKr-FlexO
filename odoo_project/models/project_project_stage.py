# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ProjectProjectStage(models.Model):
    _inherit = "project.project.stage"

    code = fields.Char(string="Code", translate=False)
