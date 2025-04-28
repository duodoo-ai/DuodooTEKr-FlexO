# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Users(models.Model):
    _inherit = "res.users"

    image_medium = fields.Binary(string="Medium-sized image", related='avatar_128', store=False, readonly=False)