# -*- coding: utf-8 -*-

import base64
import datetime

from odoo import models, fields, api, tools, _
from odoo.tools import html2plaintext, file_open, ormcache


class ResCompany(models.Model):
    _inherit = "res.company"