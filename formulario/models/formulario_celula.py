from odoo import fields,models,api


class FormularioCelula(models.Model):
    _name = 'formulario.celula'

    name = fields.Char(
        string='Nombre',
    )