from odoo import fields, api, models


class FleetFinanzaLineaCredito(models.Model):
    _name = 'fleet.finanza.linea.credito'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
    )

