# -*- coding: utf-8 -*-


from odoo import fields, models


class ResMultiPlatformNotification(models.Model):
    """
    多平台推送通知
    """

    _name = "res.multi_platform.notification"
    _description = "Multi-platform push notifications"

    name = fields.Char("Title", required=True)
    message = fields.Text("Message content", required=True)
    recipient_ids = fields.Many2many("res.users", string="Receive users")
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("failed", "Failed")], string="Status", default="draft"
    )
    push_type = fields.Selection(
        [("notice", "Notice"), ("message", "Message"), ("alert", "Alerts")],
        string="Push type",
        default="notice",
    )

    def action_send_push(self):
        """发送推送消息"""
        for record in self:
            try:
                # 构造推送数据
                push_data = {
                    "title": record.name,
                    "message": record.message,
                    "type": record.push_type,
                    "recipients": record.recipient_ids.mapped("login"),
                    "data": {
                        "notification_id": record.id,
                        "create_date": record.create_date.isoformat(),
                    },
                }

                # 发送到 WebSocket 服务器
                self._send_to_websocket_server(push_data)

                # 更新状态
                record.state = "sent"

            except Exception as e:
                _logger.error(f"推送消息失败: {str(e)}")
                record.state = "failed"
