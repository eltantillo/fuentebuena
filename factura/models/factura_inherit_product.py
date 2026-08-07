from odoo import models, fields, api


class FacturaInheritProduct(models.Model):
    _inherit = 'product.product'

    codigo_ids = fields.One2many(
        string='Codigos',
        comodel_name='product.unspsc.code',
        inverse_name='categoria_id'
    )