from odoo import fields, api, models


class RolesPiloteaMotivoCambioAgenda(models.Model):
    _name='rp.motivo.cambio.agenda'

    name = fields.Char(
        string='Nombre',
    )