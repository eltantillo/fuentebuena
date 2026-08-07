from odoo import fields, models, api


class BolsaTrabajoArea(models.Model):
    _name = 'bolsa.trabajo.area'

    name = fields.Char(
        string='Nombre',
    )