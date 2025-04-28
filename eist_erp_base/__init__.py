# -*- coding: utf-8 -*-


# from . import controllers
from . import models

from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    """
    !安装模块时，执行：
    ~ 1. 隐藏企业版应用，更新模块列表
    ~ 2. 隐藏原生应用
    """
    apps_name = ""

    # 隐藏企业版应用
    ent_modules = env["ir.module.module"].search(
        ["&", ("to_buy", "=", True), ("application", "=", True)]
    )
    # for module in ent_modules:
    #     apps_name += module.name + ","

    ent_modules.write({"application": False})
    if len(ent_modules) > 0:
        env["ir.module.module"].update_list()  # 避免打开设置页面报错

    # 隐藏原生应用
    # odoo_modules = env["ir.module.module"].search(
    #     ["&", ("is_ierp", "!=", True), ("application", "=", True)]
    # )
    # odoo_modules.write({"application": False})

    # # ”w"代表着每次运行都覆盖内容
    # with file_open(file_path, "w") as f:
    #     f.write(apps_name)
   

def uninstall_hook(env):
    """
    !卸载模块时，执行：
    ~ 1. 恢复显示隐藏企业版应用
    ~ 2. 更新模块列表
    """

    # with file_open(file_path, "r") as f:
    #     apps_text = f.read()  # 读取文件
    #     print("已恢复以下应用：{}".format(apps_text))
    #     apps = apps_text.split(",")
    #     for app in apps:
    #         ent_app = env["ir.module.module"].search([("name", "=", app)])
    #         if ent_app:
    #             ent_app.write({"application": True})
    ent_modules = env["ir.module.module"].search(
        [("to_buy", "=", True)]
    )
    ent_modules.write({"application": True})
    env["ir.module.module"].update_list()  # 避免打开设置页面报错