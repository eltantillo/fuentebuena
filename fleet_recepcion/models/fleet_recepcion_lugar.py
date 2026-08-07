from odoo import models, fields, api


class FleetRecepcionLugar(models.Model):
    _name='fleet.recepcion.lugar'
    _description='Fleet Recepcion Lugar'

    name = fields.Char(
        string='Lugar de recepcion',
    )
    active = fields.Boolean('Active', default=True, tracking=True)