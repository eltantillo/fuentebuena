from odoo import fields,models,api


class ExpedienteConfigTipo(models.Model):

    _name = 'expediente.config.tipo'

    flotilla_id = fields.Many2one(
        string='Flotilla',
        comodel_name='fleet.customer.flotilla',
    )
    producto_ids = fields.Many2many(
        string='Producto',
        comodel_name='fleet.customer.producto',
    )
    plaza_ids = fields.Many2many(
        string='Plaza',
        comodel_name='fleet.customer.plaza',
    )
    tipo_expediente_ids = fields.Many2many(
        string='Tipo Expediente',
        comodel_name='expediente.tipo',
    )