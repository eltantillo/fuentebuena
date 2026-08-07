from odoo import fields,api,models


class FormularioActividad(models.Model):
    _name = 'formulario.actividad'

    name = fields.Char(
        string='Nombre',
    )