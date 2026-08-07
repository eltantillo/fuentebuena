from odoo import fields,models,api
from odoo.exceptions import ValidationError


class FacturaMotivoCancelacion(models.Model):
    _name = 'factura.motivo.cancelacion'
    _description = 'Modelo para añadir un motivo de cancelacion para las facturas'

    name = fields.Char(
        string='Motivo de cancelacion'
    )
    motivo_duplicado = fields.Boolean(
        string = 'Motivo predefinido para facturas duplicadas',
        default = False
    )

    @api.constrains('motivo_duplicado')
    def _check_motivo_duplicado(self):
        if self.motivo_duplicado and self.search_count([('motivo_duplicado','=',  True)]) > 1:
            raise ValidationError('Solo se puede tener un motivo predefinido para facturas duplicadas.')