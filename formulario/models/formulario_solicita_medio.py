from odoo import fields,models,api


class FormularioSolicitaMedio(models.Model):
    _name = 'formulario.solicita.medio'

    name = fields.Char(
        string='Nombre',
    )
    active =fields.Boolean(
        string='Activo',
        default=True,
    )
