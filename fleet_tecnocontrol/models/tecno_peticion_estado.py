from odoo import  fields, api, models


class TecnoPeticionEstado(models.Model):
    _name = 'tecno.peticion.estado'

    name = fields.Char(
        string='Estado',
    )