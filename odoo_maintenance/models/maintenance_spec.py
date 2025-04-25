# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/03 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class MaintenanceEquipmentSpec(models.Model):
    _name = 'maintenance.equipment.spec'
    _inherit = ['mail.thread']
    _description = '技术指标'
    _order = 'effective_date desc, revision desc'

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='设备',
        required=True,
        ondelete='cascade'
    )
    parameter_type = fields.Selection([
        ('drive', '驱动参数'),
        ('power', '电气参数'),
        ('mechanical', '机械参数'),
        ('other', '其他参数')],
        string='参数类型',
        required=True
    )
    # 动态参数存储（JSON字段）
    technical_data = fields.Json('技术数据')

    # 驱动参数
    drive_type = fields.Selection([
        ('electric', '电动驱动'),
        ('hydraulic', '液压驱动'),
        ('pneumatic', '气动驱动'),
        ('mechanical', '机械驱动'),
        ('magnetic', '磁力驱动')],
        string='驱动类型'
    )
    motor_power = fields.Float('电机功率(kW)', digits=(8, 2))
    rated_speed = fields.Integer('额定转速(RPM)')

    # 支撑参数
    bearing_type = fields.Selection([
        ('rolling', '滚动轴承'),
        ('sliding', '滑动轴承'),
        ('magnetic', '磁悬浮轴承'),
        ('air', '空气轴承')],
        string='支撑类型'
    )
    bearing_life = fields.Integer('预期寿命(小时)')
    lubrication_cycle = fields.Integer('润滑周期(天)')

    # 联轴器参数
    coupling_type = fields.Selection([
        ('rigid', '刚性联轴器'),
        ('flexible', '弹性联轴器'),
        ('universal', '万向联轴器'),
        ('diaphragm', '膜片联轴器')],
        string='联轴器类型'
    )
    max_torque = fields.Float('最大扭矩(N·m)', digits=(10, 2))
    axial_compensation = fields.Float('轴向补偿量(mm)', digits=(5, 2))

    # 电气参数
    rated_power = fields.Float('额定功率(kW)', digits=(10, 2))
    rated_voltage = fields.Float('额定电压(V)', digits=(8, 2))
    power_factor = fields.Float('功率因数', digits=(3, 2))

    # 监控数据
    current_value = fields.Float('当前值', digits=(16, 4))
    unit = fields.Char('单位', size=10, default='-')
    last_updated = fields.Datetime('最后更新')

    # 版本控制
    revision = fields.Integer('版本号', default=1)
    effective_date = fields.Date('生效日期', default=fields.Date.today)
    active = fields.Boolean('生效', default=True)

    # 告警规则
    alert_rule_ids = fields.One2many(
        'maintenance.alert.rule',
        'spec_id',
        string='告警规则'
    )

    @api.constrains('effective_date')
    def _check_effective_date(self):
        for record in self:
            if record.effective_date < fields.Date.today():
                raise ValidationError(_("生效日期不能早于当前日期！"))

    @api.depends('current_value')
    def _check_value_updates(self):
        """值变更时自动触发告警检查"""
        self.check_alert_rules()

    def check_alert_rules(self):
        """告警规则检查核心方法"""
        AlertRule = self.env['maintenance.alert.rule']
        for spec in self.filtered(lambda r: r.active):
            active_rules = AlertRule.search([
                ('spec_id', '=', spec.id),
                ('active', '=', True)
            ])

            for rule in active_rules:
                current = spec.current_value
                trigger = False

                if rule.condition_type == 'min' and current < rule.min_value:
                    trigger = True
                elif rule.condition_type == 'max' and current > rule.max_value:
                    trigger = True
                elif rule.condition_type == 'range' and not (rule.min_value <= current <= rule.max_value):
                    trigger = True

                if trigger:
                    self._trigger_alert(rule, current)
                    rule.write({'last_triggered': fields.Datetime.now()})

    # 批量处理检查
    @api.model
    def _check_all_equipment_alerts(self):
        specs = self.search([('active', '=', True)])
        specs.check_alert_rules()

    def _get_notify_partners(self):
        # 自动包含设备负责人+指定人员
        return list(
            set(self.equipment_id.owner_id.ids) |
            set(self.notify_user_ids.ids)
        )

    def _trigger_alert(self, rule, current_value):
        """告警触发处理"""
        # 生成工单
        if rule.action_type in ('workorder', 'both'):
            self.env['maintenance.work.order'].create({
                'equipment_id': self.equipment_id.id,
                'type': 'corrective',
                'priority': rule.severity_level,
                'description': f'''
                【参数告警】{rule.name}
                当前值：{current_value}{self.unit}
                设备：{self.equipment_id.name}
                阈值：{rule._get_threshold_display()}
                '''
            })

        # 发送通知
        if rule.action_type in ('notification', 'both'):
            self.env['mail.message'].create({
                'subject': f'【设备告警】{self.equipment_id.name} - {rule.name}',
                'body': f'''
                <p>设备名称：{self.equipment_id.name}</p>
                <p>技术参数：{self.parameter_type}</p>
                <p>当前值：{current_value}{self.unit}</p>
                <p>触发规则：{rule.name}</p>
                ''',
                'partner_ids': [(6, 0, self._get_notify_partners())],
                'model': 'maintenance.equipment',
                'res_id': self.equipment_id.id
            })


class MaintenanceAlertRule(models.Model):
    _name = 'maintenance.alert.rule'
    _description = '设备告警规则'
    _order = 'sequence asc'

    name = fields.Char('规则名称', required=True, translate=True)
    sequence = fields.Integer('优先级', default=10)
    spec_id = fields.Many2one(
        'maintenance.equipment.spec',
        string='技术指标',
        required=True,
        ondelete='cascade'
    )
    parameter_name = fields.Char(
        '监控参数',
        compute='_compute_parameter_name',
        store=True
    )
    condition_type = fields.Selection([
        ('min', '低于最小值'),
        ('max', '超过最大值'),
        ('range', '超出范围')],
        string='条件类型',
        default='max'
    )
    min_value = fields.Float('阈值下限')
    max_value = fields.Float('阈值上限')
    action_type = fields.Selection([
        ('notification', '发送通知'),
        ('workorder', '生成工单'),
        ('both', '通知+工单')],
        string='触发动作',
        default='both'
    )
    severity_level = fields.Selection([
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('critical', '紧急')],
        string='严重等级',
        default='medium'
    )
    active = fields.Boolean('启用', default=True)
    last_triggered = fields.Datetime('最后触发时间')
    notify_user_ids = fields.Many2many(
        'res.users',
        string='通知人员'
    )

    @api.depends('spec_id.parameter_type')
    def _compute_parameter_name(self):
        for record in self:
            if record.spec_id:
                record.parameter_name = dict(
                    record.spec_id._fields['parameter_type'].selection
                ).get(record.spec_id.parameter_type)

    def _get_threshold_display(self):
        self.ensure_one()
        if self.condition_type == 'min':
            return f"≥ {self.min_value}"
        elif self.condition_type == 'max':
            return f"≤ {self.max_value}"
        else:
            return f"{self.min_value} ~ {self.max_value}"

    @api.constrains('min_value', 'max_value')
    def _check_thresholds(self):
        for rule in self:
            if rule.condition_type == 'range' and rule.min_value >= rule.max_value:
                raise ValidationError(_("阈值下限必须小于上限"))


# class MaintenanceEquipment(models.Model):
#     _inherit = 'maintenance.equipment'
#
#     spec_ids = fields.One2many(
#         'maintenance.equipment.spec',
#         'equipment_id',
#         string='技术指标'
#     )
    # active_alert_count = fields.Integer(
    #     '活跃告警',
    #     compute='_compute_active_alerts'
    # )

    # def _compute_active_alerts(self):
    #     AlertRule = self.env['maintenance.alert.rule']
    #     for equipment in self:
    #         equipment.active_alert_count = AlertRule.search_count([
    #             ('spec_id.equipment_id', '=', equipment.id),
    #             ('active', '=', True)
    #         ])