from odoo import fields,models,api


class GastoOperativoInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    gasto_operativo_ids = fields.One2many(
        comodel_name='gasto.operativo',
        inverse_name='vehiculo_id',
        string='Gasto Operativos',
    )