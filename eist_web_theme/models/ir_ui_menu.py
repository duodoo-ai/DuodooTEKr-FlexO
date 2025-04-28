# -*- coding: utf-8 -*-


import re

from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def load_web_menus(self, debug):
        """
        加载所有菜单项（所有应用程序及其子菜单）并处理它们以供 Web 客户端使用。
        主要是，它与每个应用程序（顶级菜单）关联其第一个子菜单的操作，该操作与操作（递归）相关联，即与打开应用程序时要执行的操作相关联。

        :return:  菜单（包括 Base64 中的图片）
        """
        web_menus = super(IrUiMenu, self).load_web_menus(debug)
        
        return web_menus
