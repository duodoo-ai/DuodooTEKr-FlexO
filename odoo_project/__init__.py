# -*- coding: utf-8 -*-

from . import models
from . import controllers


def _odoo_project_post_init(env):
    """
    项目初始化
    """
    env["res.config.settings"].create({"group_project_stages": True}).execute()


def _odoo_project_uninstall_hook(env):
    """
    项目卸载
    """
    parameters = (
        env["ir.config_parameter"].sudo().search([("key", "=like", "water_supply_pipeline%")], limit=None)
    )

    if parameters:
        for parameter in parameters:
            parameter.unlink()
