from odoo import fields,models,api


class FormularioRegion(models.Model):
    _name = 'formulario.region'

    name = fields.Char(
        string='Nombre',
    )