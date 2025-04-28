# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/17 11:20
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company:
"""
import requests
import json
import logging
import datetime
from odoo import fields, models
_logger = logging.getLogger(__name__)


class PhoenixToken(models.Model):
    _name = 'phoenix.token'
    _description = '获取PhoenixAPI网关接口调用token'

    # 请求内容
    name = fields.Char(string='Auth接口名称', default='获取PhoenixAPI网关接口调用token', help='API名称')
    grant_type = fields.Char(string='后端请求类型', default='password', help='必填。后端请求类型')
    username = fields.Char(string='登录用户', default='admin', help='必填。Observer系统登录用户')
    password = fields.Char(string='登录密码', default='admin', help='必填。Observer系统登录密码')
    url = fields.Char(string='接口地址', default='http://192.168.43.16', help='必填。接口地址')
    port = fields.Char(string='接口端口', default='14050', help='接口端口')
    # 返回内容
    access_token = fields.Char(string='access_token', help=' ')
    token_type = fields.Char(string='token_type', help=' ')
    expires_in = fields.Char(string='expires_in', help=' ')
    refresh_token = fields.Char(string='refresh_token', help=' ')
    msg = fields.Char(string='接口请求结果', help='返回code，成功success ')
    # 描述
    description = fields.Char(string='description',
                              default='Use granttype=refresh_token and fill in refresh_token value to refresh token, '
                                      'also user can set in observer the token timeout. If you login first time then '
                                      'use granttype=password + username and password')

    active = fields.Boolean(string='启用', default=True)
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    def action_token_from_phoenix(self):
        # ===========================Token===============================
        # Step1：配置host地址、端口号、appKey和appSecret
        # api config
        phoenix = self.env['phoenix.token'].search([('name', '=', '获取PhoenixAPI网关接口调用token')])
        url_token = '{}'.format(phoenix.url + ':' + phoenix.port + '/token')

        # Step2：Setting Headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Step3：拼接访问权限
        data = ("grant_type={}&username={}&password={}"
                .format(phoenix.grant_type, phoenix.username, phoenix.password))

        try:
            # Step4：发送POST请求
            response = requests.post(url_token, headers=headers, data=data)
            # Step5：打印响应内容
            token = json.loads(response.text)
            current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            pv = {
                'access_token': token['access_token'],
                'token_type': token['token_type'],
                'expires_in': token['expires_in'],
                'refresh_token': token['refresh_token'],
                'msg': '获取TOKEN成功！' + '  最近更新时间 ( {} )'.format(current_time.strftime('%Y-%m-%d %H:%M:%S')),
            }
            if phoenix:
                phoenix.write(pv)
        except Exception as e:
            _logger.error(f'声光TOKEN报错：{e}')
            return

