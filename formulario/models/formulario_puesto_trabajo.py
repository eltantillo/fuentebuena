from odoo import fields,models,api


class FormularioPuestoTrabajo(models.Model):
    _name = 'formulario.puesto.trabajo'

    name = fields.Char(
        string="Nombre",
    )