
from odoo import fields, models, api

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    fb_agreement_id = fields.Many2one('fb.agreement', string='Convenio', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        agreement_id = self.fb_agreement_id
        if agreement_id:
            for vals in vals_list:
                vals.setdefault('fb_agreement_id', agreement_id.id)
        return super().create(vals_list)