# -*- coding: utf-8 -*-
"""
@Time    : 2024/09/20 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
import os, io
import logging
import qrcode
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import http
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    complete_path = fields.Char(string='Complete Path', copy=False)  # 完整名称
    parent_id = fields.Many2one('maintenance.equipment', string='Hierarchy')  # 目录树
    child_ids = fields.One2many('maintenance.equipment', 'parent_id', string='Sub Hierarchy')  # 下级目录

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """上级目录不能选择自己和下级的目录"""
        for s in self:
            if s.parent_id:
                nodes = s.env['maintenance.equipment'].search([('parent_id', '=', s.id)])
                if s.parent_id in nodes:
                    raise UserError('The superior directory cannot select himself or his subordinate directory')

    # 新增字段，管理设备的生命周期，从采购、安装、使用、维护到退役的各个阶段
    purchase_date = fields.Date(string='Purchase Date')     # 采购日期
    installation_date = fields.Date(string='Installation Date')     # 安装日期
    first_use_date = fields.Date(string='First Use Date')     # 首次使用日期
    last_maintenance_date = fields.Date(string='Last Maintenance Date')     # 最后维护日期
    expected_retirement_date = fields.Date(string='Expected Retirement Date')     # 预计退役日期
    lifecycle_state = fields.Selection([
        ('purchasing', 'Purchasing'),
        ('installing', 'Installing'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired')
    ], string='Lifecycle State', default='purchasing')     # 生命周期状态
    equipment_state = fields.Selection(
        [('normal', 'In Progress'), ('warn', 'In Warn'), ('alarm', 'To Alarm')],
        string='Running State', required=True, default='normal', tracking=True) # 设备运行状态

    spec_ids = fields.One2many(
        'maintenance.equipment.spec',
        'equipment_id',
        string='技术指标'
    )
    active_alerts = fields.Integer(
        '活跃告警',
        compute='_compute_active_alerts'
    )

    def _compute_active_alerts(self):
        for equip in self:
            equip.active_alerts = self.env['maintenance.alert.rule'].search_count([
                ('spec_id.equipment_id', '=', equip.id),
                ('active', '=', True)
            ])

    barcode = fields.Char(string="QR Code Text")
    qr_code = fields.Binary(string="QR Code", attachment=True, compute='_compute_qr_code', store=True)
    qr_context = fields.Text(string="QR Context")

    def generate_qr_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/equipment/{self.id}"

    @api.depends('barcode')
    def _compute_qr_code(self):
        for record in self:
            try:
                if record.barcode:
                    # 生成二维码逻辑
                    qr = qrcode.QRCode(
                        version=3,  # 提升版本支持更多数据
                        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 提高容错率
                        box_size=20,  # 增大单个模块尺寸
                        border=2,  # 减少边框占用空间
                    )
                    qr.add_data(record.generate_qr_url())
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="#2E7D32", back_color="#FFFFFF")
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG", dpi=(300, 300))
                    record.qr_code = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    record.qr_context = base64.b64encode(buffer.getvalue()).decode('utf-8')
                else:
                    record.qr_code = False
            except Exception as e:
                _logger.error(f"生成二维码失败: {str(e)}")
                record.qr_code = False

    def action_print_qrcode(self):
        return self.env.ref('odoo_maintenance.report_maintenance_qrcode').report_action(self)

    def action_batch_print_qr(self):
        return self.env.ref('odoo_maintenance.report_maintenance_qr').report_action(self.ids)

    inspection_ids = fields.One2many(
        'maintenance.inspection',
        'equipment_id',
        string='巡检记录'
    )

    def action_open_inspection(self):
        """ 通过按钮触发时强制注入上下文 """
        return {
            'type': 'ir.actions.act_window',
            'name': '巡检记录',
            'res_model': 'equipment.inspection',
            'context': {
                'default_equipment_id': self.id,
                'search_equipment_id': self.id
            },
            'view_mode': 'list,form',
            'target': 'current'
        }

    def action_scan_qr(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'open_qr_scanner',
            'target': 'new',
            'context': {
                'default_model': 'maintenance.equipment',
                'default_res_id': self.id,
            }
        }

    # 临时使用通用客户端动作
    # def action_scan_qr(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': '扫码巡检',
    #         'res_model': 'maintenance.equipment',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'qr_scan_mode': True}
    #     }

    monitoring_data_ids = fields.One2many(
        'equipment.monitoring.data',
        'equipment_id',
        string='Bind device'
    )
    last_monitoring = fields.Datetime(
        '最后上传时间',
        compute='_compute_last_monitoring'
    )

    def _compute_last_monitoring(self):
        for record in self:
            last = self.env['equipment.monitoring.data'].search([
                ('equipment_id', '=', record.id)
            ], order='write_date desc', limit=1)
            record.last_monitoring = last.timestamp if last else False

    latest_gsm_longitude = fields.Float(
        'Gsm Longitude',
        digits='Gsm'
    )
    latest_gsm_latitude = fields.Float(
        'Gsm Latitude',
        digits='Gsm'
    )
    latest_pressure = fields.Float(
        'Pressure(kPa)',
        digits='Pressure',
        tracking=True
    )
    # 流体监测
    latest_flow_rate = fields.Float(
        'Traffic(m³/h)',
        digits='Traffic',
        tracking=True
    )
    latest_liquid_level = fields.Float(
        'Liquid level(m)',
        digits='Liquid',
        tracking=True
    )


class EquipmentInspection(models.Model):
    _name = 'equipment.inspection'
    _inherit = ['mail.thread']
    _description = '设备巡检记录'

    @api.constrains('equipment_id')
    def _check_equipment_id(self):
        for record in self:
            if not record.equipment_id:
                raise ValidationError("必须关联设备！")

    equipment_id = fields.Many2one('maintenance.equipment', required=True,
                                   default=lambda self: self._get_equipment_id()
                                   )

    _sql_constraints = [
        ('equipment_index',
         'INDEX (equipment_id)',
         '加速设备关联查询')
    ]

    def _get_equipment_id(self):
        """安全获取设备ID的三级回退策略"""
        ctx = self.env.context

        # 1. 从按钮显式传递的上下文获取
        if 'default_equipment_id' in ctx:
            return ctx['default_equipment_id']

        # 2. 从绑定模型动作获取
        if ctx.get('active_model') == 'maintenance.equipment':
            return ctx.get('active_id')

        # 3. 从URL参数获取（支持外部系统集成）
        return False

    inspection_date = fields.Datetime(string='Inspection Date', default=fields.Datetime.now)
    operator_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    status = fields.Selection([
        ('normal', '正常'),
        ('warning', '异常待处理'),
        ('danger', '紧急停机')
    ], required=True)
    notes = fields.Text('巡检备注')
    image = fields.Binary('现场照片')
    location = fields.Char('GPS位置', help="通过移动设备自动获取位置信息")

    @api.model
    def create(self, vals):
        if not vals.get('equipment_id'):
            raise UserError("必须选择设备！")
        return super().create(vals)

    @api.constrains('equipment_id')
    def _check_equipment_id(self):
        for record in self:
            if not record.equipment_id:
                raise ValidationError(_(
                    "设备关联失败！\n"
                    "可能原因：\n"
                    "1. 未从设备详情页触发操作\n"
                    "2. URL参数缺失设备ID\n"
                    "3. 手动创建时未选择设备"
                ))

    def action_create_request(self):
        """自动生成维修工单"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': '创建维修工单',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_equipment_id': self.equipment_id.id,
                'default_description': f'巡检发现问题：{self.notes}'
            }
        }
