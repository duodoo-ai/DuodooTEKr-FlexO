# -*- coding: utf-8 -*-
"""
@Time    : 2025/02/27 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
import ast
from odoo import models, fields, api


class DtuData(models.Model):
    _inherit = 'dtu.data'

    @api.model
    def cron_compute_dtu_aggregate(self):
        # Global traffic summary statistics 全局流量 汇总统计
        # Global traffic summary statistics 全局流量 汇总统计
        # Global traffic summary statistics 全局流量 汇总统计
        stats = {}
        # Total statistics 总计统计
        total_traffic = self.search_read([], ['traffic'])
        stats['total'] = sum([record['traffic'] for record in total_traffic if record['traffic']])

        try:
            # 按月统计 - Monthly statistics
            monthly_stats = self.env['dtu.data'].read_group(
                [('time', '!=', False)],
                ['traffic:sum'],
                ['time:month']
            )
            stats['monthly'] = {record['time:month']: record['traffic'] for record in monthly_stats}
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Monthly statistics error: {e}")
            stats['monthly'] = {}

        try:
            # 按季统计 - Quarterly statistics
            quarterly_stats = self.env['dtu.data'].read_group(
                [('time', '!=', False)],
                ['traffic:sum'],
                ['time:quarter']
            )
            stats['quarterly'] = {record['time:quarter']: record['traffic'] for record in quarterly_stats}
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Seasonal statistics error: {e}")
            stats['quarterly'] = {}

        try:
            # 按年统计 - Annual statistics
            yearly_stats = self.env['dtu.data'].read_group(
                [('time', '!=', False)],
                ['traffic:sum'],
                ['time:year']
            )
            stats['yearly'] = {record['time:year']: record['traffic'] for record in yearly_stats}
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Annual statistics error: {e}")
            stats['yearly'] = {}

        print("Final statistical results:", stats)
        return stats

    @api.model
    def cron_compute_dtu_aggregate_by_project(self):
        """按项目名称(name)统计流量数据，包括总流量、月度流量、季度流量和年度流量"""

        stats = {
            'name_total': {},
            'name_monthly': {},
            'name_quarterly': {},
            'name_yearly': {}
        }

        try:
            # 1. 按项目名称统计总流量
            total_stats = self.env['dtu.data'].read_group(
                [('name', '!=', False), ('traffic', '!=', False)],
                ['traffic:sum', 'name'],
                ['name'],
                lazy=False
            )
            stats['name_total'] = {rec['name']: rec['traffic'] for rec in total_stats}

            # 2. 按项目名称+月份统计流量
            monthly_stats = self.env['dtu.data'].read_group(
                [('name', '!=', False), ('time', '!=', False), ('traffic', '!=', False)],
                ['traffic:sum', 'name'],
                ['name', 'time:month'],  # 正确的分组语法
                lazy=False
            )
            # print("按月统计原始数据：", monthly_stats)  # 调试输出

            for rec in monthly_stats:
                name = rec['name']
                month = rec['time:month']  # 格式示例："January 2023"
                if name not in stats['name_monthly']:
                    stats['name_monthly'][name] = {}
                stats['name_monthly'][name][month] = rec['traffic']

            # 3. 按项目名称+季度统计流量
            quarterly_stats = self.env['dtu.data'].read_group(
                [('name', '!=', False), ('time', '!=', False), ('traffic', '!=', False)],
                ['traffic:sum', 'name'],
                ['name', 'time:quarter'],  # 正确的分组语法
                lazy=False
            )
            # print("按季度统计原始数据：", quarterly_stats)  # 调试输出

            for rec in quarterly_stats:
                name = rec['name']
                quarter = rec['time:quarter']  # 格式示例："Q1 2023"
                if name not in stats['name_quarterly']:
                    stats['name_quarterly'][name] = {}
                stats['name_quarterly'][name][quarter] = rec['traffic']

            # 4. 按项目名称+年份统计流量
            yearly_stats = self.env['dtu.data'].read_group(
                [('name', '!=', False), ('time', '!=', False), ('traffic', '!=', False)],
                ['traffic:sum', 'name'],
                ['name', 'time:year'],  # 正确的分组语法
                lazy=False
            )
            # print("按年统计原始数据：", yearly_stats)  # 调试输出

            for rec in yearly_stats:
                name = rec['name']
                year = rec['time:year']  # 格式示例："2023"
                if name not in stats['name_yearly']:
                    stats['name_yearly'][name] = {}
                stats['name_yearly'][name][year] = rec['traffic']

        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"统计出错：{str(e)}", exc_info=True)
            # 保持原有结构，即使出错也返回空字典
            stats = {
                'name_total': {},
                'name_monthly': {},
                'name_quarterly': {},
                'name_yearly': {}
            }

        # print("最终统计结果：", stats)

        # # 更新项目汇总值
        self.update_project_map_location(stats)

        return stats

    def update_project_map_location(self, stats):
        project_obj = self.env['project.project']
        project_records = project_obj.search([])
        monthly_traffic = 0
        seasonal_traffic = 0
        year_traffic = 0
        total_traffic = 0
        for line in project_records:
            # 循环输出各统计维度下的值
            for stats_type, routes in stats.items():
                for route, data in routes.items():
                    if stats_type == 'name_total' and route == line.name:
                        total_traffic = data
                    if isinstance(data, dict):
                        for period, value in data.items():
                            if stats_type == 'name_monthly' and route == line.name:
                                monthly_traffic = value
                            if stats_type == 'name_quarterly' and route == line.name:
                                seasonal_traffic = value
                            if stats_type == 'name_yearly' and route == line.name:
                                year_traffic = value
            uv = {
                'name': line.name,
                'monthly_traffic': monthly_traffic,
                'seasonal_traffic': seasonal_traffic,
                'year_traffic': year_traffic,
                'total_traffic': total_traffic,
            }
            print(f'uv -----{uv}')
            line.write(uv)



