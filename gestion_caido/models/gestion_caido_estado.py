from odoo import fields,models,api


class GestionCaidoEstado(models.Model):

    _name = 'gestion.caido.estado'
    _order = 'sequence'

    name = fields.Char(
        string='Nombre'
    )
    sequence = fields.Integer(
        string='Sequence',
    )