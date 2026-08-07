from odoo import fields,models,api


class PromesasPFrecuenciaNomina(models.Model):
    _name = 'promesa.p.frecuencia.nomina'

    name = fields.Char(
        string='Nombre'
    )
    nombre_corto = fields.Char(
        string='Nombre Corto'
    )
    factor = fields.Char(
        string='Factor',
    )