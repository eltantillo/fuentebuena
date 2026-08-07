from odoo import fields,api,models


class FacturaAccountMoveLinea(models.Model):
    _inherit = 'account.move.line'
    _description = 'Herencia para agregar campos en las lineas de factura'

    descripcion = fields.Char(
        string='Descripcion',
    )
    codigo_id = fields.Many2one(
        comodel_name='product.unspsc.code',
        string='Código SAT',
    )
    codigo_sat = fields.Char(
        string='Código SAT',
    )