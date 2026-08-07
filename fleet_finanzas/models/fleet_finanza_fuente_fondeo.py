from odoo import fields,api,models


class FleetFinanzaFuenteFondeo(models.Model):
    _name = 'fleet.finanza.fuente.fondeo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
    )