from odoo import fields,models,api


class FormularioAyuntamiento(models.Model):
    _name = 'formulario.ayuntamiento'

    name = fields.Char(
        string='Nombre'
    )
    estado_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
