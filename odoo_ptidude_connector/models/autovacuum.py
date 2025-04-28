# -*- coding: utf-8 -*-
"""
@Time    : 2024/10/22 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: 多度信息科技（南京）有限公司
"""
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CollectAutovacuum(models.TransientModel):
    _name = "collect.autovacuum"
    _description = "删除采集旧数据"

    @api.model
    def autovacuum(self, days):
        """Delete all logs older than ``days``. This includes:
            - Traffic
        Called from a cron.
        """
        days = (days > 0) and int(days) or 0
        deadline = datetime.now() - timedelta(days=days)
        records = self.env["phoenix.dynamic.measurements"].search(
            [("create_date", "<=", fields.Datetime.to_string(deadline))]
        )
        nb_records = len(records)
        records.unlink()    # 删除告警运行日志表
        _logger.info("告警日志 - %s '%s' 告警日志已删除", nb_records, "phoenix.dynamic.measurements")
        return True
