from odoo import models,fields,api


class MantenimientoTiProveedor(models.Model):
    _name = 'mantenimiento.ti.proveedor'

    name = fields.Char(
        string="Nombre"
    )
    monto_ultimo_pago = fields.Float(
        string="Monto ultimo pago"
    )