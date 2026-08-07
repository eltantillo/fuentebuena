from odoo import fields,models


class PuestoOcupado(models.Model):
    _name = 'puesto.ocupado'
    _description = 'Puesto Ocupado'

    name = fields.Char(
        string='Nombre',
        required=True
    )

