from odoo import  fields,models,api


class GastoOperativoMotivo(models.Model):
    _name = 'gasto.operativo.motivo'

    name = fields.Char(
        string='Motivo',
    )