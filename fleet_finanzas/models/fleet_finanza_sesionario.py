from odoo import fields, api, models


class FleetFinanzaSesionario(models.Model):
    _name = 'fleet.finanza.sesionario'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
    )