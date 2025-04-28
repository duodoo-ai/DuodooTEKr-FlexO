# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, tools, _
from odoo.addons.base.models.res_users import check_identity


class ResUsers(models.Model):
    _inherit = "res.users"

    lock_screen = fields.Boolean(string="Lock Screen", default=False)

    theme_id = fields.Many2one(
        "res.theme", string="Theme", store=True, domain="[('user_id', '=', id)]"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        创建新用户时，创建主题
        """
        users = super(ResUsers, self).create(vals_list)
        for new_user in users:
            new_user.theme_id = (  # type: ignore
                self.env["res.theme"].sudo()._get_or_create_theme(new_user.id, "user")  # type: ignore
            )
        return users

    # @api.model
    # def set_user_theme(self, uid, theme):
    def set_user_theme(self):
        """
        设置用户主题
        :param uid: 用户id
        :param theme: 主题名称
        :return:
        """
        # user_id = self.env.context.get("uid")
        theme = self.env.context.get("theme")
        # user = self.sudo().browse(uid)
        # print(self)
        # print(user_id)
        # print(theme,type(theme))
        self.theme_id.sudo().write(theme)

    # @api.model
    # def signup(self, values, token=None):
    #     """
    #     注册用户，以便：
    #         - 创建一个新用户（无令牌），或
    #         - 为合作伙伴创建用户（使用令牌，但没有合作伙伴的用户），或
    #         - 更改用户的密码（使用令牌和现有用户）。
    #         :param values:一个字典，其中包含写入用户的字段值
    #         :param token:注册令牌（可选）
    #         :return: (dbname, login, password) 对于已注册的用户
    #     """
    #     res = super(ResUsers, self).signup(values, token)
    #     print(values)
    #     return res
