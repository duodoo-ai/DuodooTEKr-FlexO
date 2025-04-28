# coding: utf-8

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class BaseImport(models.TransientModel):
    _inherit = 'base_import.import'