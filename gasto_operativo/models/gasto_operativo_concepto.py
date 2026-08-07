from odoo import  fields,models,api


class GastoOperativoConcepto(models.Model):
    _name = 'gasto.operativo.concepto'

    name = fields.Char(
        string='Concepto',
    )
    motivo_ids = fields.Many2many(
        comodel_name='gasto.operativo.motivo',
        string='Motivos',
    )