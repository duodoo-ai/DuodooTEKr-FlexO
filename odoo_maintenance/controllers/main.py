import logging
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


class EquipmentInspectionController(http.Controller):

    @http.route('/web#equipment_id=<int:equipment_id>', type='http', auth='user')
    def redirect_with_equipment(self, equipment_id, **kw):
        return request.redirect(
            f'/web#action={action_id}&model=equipment.inspection&equipment_id={equipment_id}'
        )


class InspectionController(http.Controller):

    @http.route('/web/action/load', type='json', auth="user")
    def action_load(self, action_id, additional_context=None):
        """ 全局动作加载拦截器（Odoo 18 兼容版）"""
        try:
            action = http.request.env['ir.actions.act_window'].browse(action_id)
        except Exception as e:
            _logger.error("动作加载失败 - ID: %s, 错误: %s", action_id, str(e))
            raise

        # 获取标准上下文
        context = dict(http.request.env.context)

        # 自动补全设备ID上下文
        if action.res_model == 'equipment.inspection':
            context.setdefault(
                'search_equipment_id',
                http.request.session.get('equipment_id') or  # 从会话获取
                http.request.params.get('equipment_id')  # 从URL参数获取
            )

        # 返回更新后的动作数据
        return action.read()[0]

    @http.route('/equipment/set', type='json', auth="user")
    def set_equipment_session(self, equipment_id):
        """ 设置设备ID到会话 """
        http.request.session['equipment_id'] = equipment_id
        return {'status': 'success'}
