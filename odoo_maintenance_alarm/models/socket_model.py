# -*- coding: utf-8 -*-
"""
@Time    : 2024/09/20 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@mobile  : 18951631470
"""
import socket, os
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class SocketServerStart(models.Model):
    _name = 'socket.server.start'
    _description = '485通讯协议指令集'

    name = fields.Char(string='指令地址码', required=True)
    action = fields.Char(string='指令动作', required=True)
    code = fields.Char(string='指令代码', required=True)
    active = fields.Boolean(string='启用', default=True)
    type = fields.Selection([
        ('connector', '连接设备'), ('platform', '平台动作'), ('control', '控制设备')
    ], string='类型')
    note = fields.Char(string='备注')
    state = fields.Char(string='执行状态')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # def unlink(self):
    #     for record in self:
    #         if record.note:
    #             raise UserError('不能删除系统创建的类别')

    def action_clear_alarm(self):
        """
        操作设备：手动方式 （通过命令（地址码）清除平台异常告警信息
        """
        alarm_obj = self.with_user(1).env['phoenix.alarm.pool']
        alarm_records = alarm_obj.search([])
        if len(alarm_records):
            alarm_records.write({'active': False})
        self.close_alarm_value_to_socket()
        _logger.info("{}".format('告警异常已清除'))

    def cron_auto_todo_alarm(self):
        """
        异常告警：定时去拿异常信息去驱动声光报警器告警异常
        """
        alarm_obj = self.env['phoenix.alarm.pool']
        alarm_records = alarm_obj.search([])
        if len(alarm_records):
            alarm_records.write({'active': False})
        self.open_alarm_value_to_socket()
        _logger.info("{}".format('任务已发起告警'))

    def connect_to_device(self, ip, port):
        """
        连接到设备
        :param ip: 设备的 IP 地址
        :param port: 设备的端口号
        :return: 连接对象或 None
        """
        try:
            # 创建 Socket 对象
            socket_server = socket.socket()
            # 绑定 IP 地址和端口
            socket_server.bind((ip, port))
            # 监听端口
            socket_server.listen(1)
            print(f"正在监听 {ip}:{port}...")
            # 等待客户端连接
            conn, address = socket_server.accept()
            print(f"接收到了客户端的连接，客户端的信息是：{address}")
            return conn, socket_server
        except Exception as e:
            print(f"连接设备时发生异常: {e}")
            return None, None

    def send_command_to_device(self, conn, command):
        """
        向设备发送指令
        :param conn: 连接对象
        :param command: 要发送的指令
        """
        try:
            # 发送指令
            conn.send(command)
            print(f"已发送指令: {command.hex()}")
            # 接收设备的响应
            response = conn.recv(1024)
            if response:
                print(f"接收到设备的响应：{response.hex()}")
        except Exception as e:
            print(f"发送指令时发生异常: {e}")

    def send_value_to_socket(self):
        # 设备的 IP 地址和端口号
        device_obj = self.env['phoenix.audible.address']
        device_record = device_obj.search([('name', '=', '指定声光设备地址')])
        ip = device_record.ip
        port = int(device_record.port)

        # 连接到设备
        conn, socket_server = self.connect_to_device(ip, port)      # 连接到设备
        if conn and socket_server:
            try:
                # 发送指令
                self.send_command_to_device(conn, bytes.fromhex(self.name))      # 向设备发送指令
            except KeyboardInterrupt:
                print("用户手动中断程序")
            finally:
                # 关闭连接
                conn.close()
                socket_server.close()
                print("连接已关闭")

    def open_alarm_value_to_socket(self):
        # 设备的 IP 地址和端口号
        device_obj = self.env['phoenix.audible.address']
        device_record = device_obj.search([('name', '=', '指定声光设备地址')])
        ip = device_record.ip
        port = int(device_record.port)
        # 查找：	打开声音和灯光 指令动作
        action_record = self.env['socket.server.start'].search([('action', '=', '打开声音和灯光')]).name

        # 连接到设备
        conn, socket_server = self.connect_to_device(ip, port)      # 连接到设备
        if conn and socket_server:
            try:
                # 发送指令
                self.send_command_to_device(conn, bytes.fromhex(action_record))      # 向设备发送指令
            except KeyboardInterrupt:
                print("用户手动中断程序")
            finally:
                # 关闭连接
                conn.close()
                socket_server.close()
                print("连接已关闭")

    def close_alarm_value_to_socket(self):
        # 设备的 IP 地址和端口号
        device_obj = self.env['phoenix.audible.address']
        device_record = device_obj.search([('name', '=', '指定声光设备地址')])
        ip = device_record.ip
        port = int(device_record.port)
        # 查找：	打开声音和灯光 指令动作
        action_record = self.env['socket.server.start'].search([('action', '=', '清除告警')]).name

        # 连接到设备
        conn, socket_server = self.connect_to_device(ip, port)      # 连接到设备
        if conn and socket_server:
            try:
                # 发送指令
                self.send_command_to_device(conn, bytes.fromhex(action_record))      # 向设备发送指令
            except KeyboardInterrupt:
                print("用户手动中断程序")
            finally:
                # 关闭连接
                conn.close()
                socket_server.close()
                print("连接已关闭")
