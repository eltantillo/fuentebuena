from odoo import fields, models, api, _

class FleetMovimientoMiscTipo(models.Model):
    _name = 'fleet.movimiento.misc.tipo'
    _description = 'Tipos de movimientos miscelaneos'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    active = fields.Boolean('Active', default=True, tracking=True)