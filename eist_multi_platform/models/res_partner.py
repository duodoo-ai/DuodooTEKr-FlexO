from odoo import fields, models

class Partners(models.Model):
    _inherit = 'res.partner'

    # 与 < 13.0 的向后兼容性相关
    image_medium = fields.Binary(string="Medium-sized image", related='avatar_128', store=False, readonly=True)
