from odoo import http
from odoo.http import request


class EquipmentInspectionController(http.Controller):

    @http.route('/equipment/inspection/<int:equipment_id>', type='http', auth="user")
    def inspection_form(self, equipment_id, **kwargs):
        equipment = request.env['maintenance.equipment'].browse(equipment_id)
        if not equipment.exists():
            return request.not_found()

        return request.render('odoo_maintenance.inspection_form_template', {
            'equipment': equipment,
            'user': request.env.user
        })

    @http.route('/equipment/submit_inspection', type='json', auth="user")
    def submit_inspection(self, **post):
        inspection_data = {
            'equipment_id': int(post.get('equipment_id')),
            'status': post.get('status'),
            'notes': post.get('notes'),
            'image': post.get('image').split(',')[1] if post.get('image') else False
        }

        inspection = request.env['equipment.inspection'].create(inspection_data)

        if inspection.status == 'warning':
            inspection.action_create_request()

        return {
            'success': True,
            'message': '巡检记录已提交',
            'inspection_id': inspection.id
        }