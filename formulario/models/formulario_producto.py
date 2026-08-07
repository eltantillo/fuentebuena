from odoo import fields,models,api


class FormularioProducto(models.Model):
    _name = 'formulario.producto'

    name = fields.Char(
        string='Nombre',
    )