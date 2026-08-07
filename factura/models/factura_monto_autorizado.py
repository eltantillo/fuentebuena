from odoo import fields,models


class FacturaMontoAutorizado(models.Model):
    _name = 'factura.monto.autorizado'
    _description = 'Modelo para vincular los grupos con los montos autorizados, utilies en la validación de las facturas'

    grupo = fields.Selection([
        ('director', 'Director'),
        ('gerente', 'Gerente'),
        ('usuario_factura', 'Usuario Factura'),
        ],
        string='Grupo de usuarios',
        required=True,
    )
    monto_autorizado = fields.Float(
        string='Monto autorizado',
        required=True,
    )

