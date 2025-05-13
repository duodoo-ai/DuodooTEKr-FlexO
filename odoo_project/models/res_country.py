# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class Country(models.Model):
    _inherit = "res.country"


class CountryState(models.Model):
    _inherit = "res.country.state"
