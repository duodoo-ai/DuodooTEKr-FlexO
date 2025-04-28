# -*- coding: utf-8 -*-

from odoo import fields, models


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('route_map', "Route Map")])

    def _get_view_info(self):
        return {'route_map': {'icon': 'fa fa-map-marker'}} | super()._get_view_info()
