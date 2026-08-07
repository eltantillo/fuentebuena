from odoo import fields,models,api

class FleetAdecuacionConfig(models.Model):
    _name = 'fleet.adecuacion.config'

    plaza_id = fields.Many2one(
        string='Plaza',
        comodel_name='fleet.customer.plaza',
    )
    tipo_adecuacion_id = fields.Many2one(
        string='Tipo de Adecuacion',
        comodel_name='fleet.adecuacion.catalogo',
    )
    importe = fields.Float(
        string='Importe',
    )
    proveedor_id = fields.Many2one(
        string='Proveedor',
        comodel_name='res.partner',
        domain=[('es_proveedor', '=', True)],
    )