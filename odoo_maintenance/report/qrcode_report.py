from odoo import models

class QRReport(models.AbstractModel):
    _name = 'report.odoo_maintenance.qr_template'
    _description = 'QR Code Report'

    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'maintenance.equipment',
            'docs': self.env['maintenance.equipment'].browse(docids),
        }