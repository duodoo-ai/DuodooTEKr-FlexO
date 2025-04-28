# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import config


class ResPartner(models.Model):
    _inherit = "res.partner"

    def geo_localize(self):
        res = super().geo_localize()

        
        return res