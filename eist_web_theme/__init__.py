# -*- coding: utf-8 -*-

from . import controllers
from . import models

from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    # ! 在安装好模块之后：
    # ~ 1. 设置所有公司的默认主题
    # ~ 2. 设置所有公司对应的系统用户的默认用户菜单项目
    # ~ 3. 设置系统用户的默认主题，
    # ~ 4. 跳转 "设置" 菜单
    domain = ["|", ("active", "=", False), ("active", "=", True)]

    companies = env["res.company"]
    theme_companies = companies.search([("theme_id", "=", False)])
    menuitem_companies = companies.search([("menuitem_id", "=", False)])

    users = env["res.users"].search(
        domain + [("theme_id", "=", False), ("groups_id", "=", 1)]
    )

    for company in theme_companies:
        company.theme_id = (
            env["res.theme"].sudo()._get_or_create_theme(company.id, "company")
        )

    for company in menuitem_companies:
        company.menuitem_id = (
            env["res.user.menuitems"].sudo()._get_or_create_menuitems(company.id)
        )
    for user in users:
        user.theme_id = env["res.theme"].sudo()._get_or_create_theme(user.id, "user")

    # env["res.company"].clear_caches()
    # env["res.users"].clear_caches()
    # env["ir.asset"].registry.clear_cache()


def uninstall_hook(env):
    """
    卸载模块时，删除所有有关主题的设置
    """
    parameters = (
        env["ir.config_parameter"]
        .sudo()
        .search([("key", "=like", "eist_erp%")], limit=None)
    )

    if parameters:
        for parameter in parameters:
            parameter.unlink()
    # env["res.company"].clear_caches()
    # env["res.users"].clear_caches()
    # env["ir.asset"].registry.clear_cache()
