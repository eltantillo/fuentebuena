from odoo import  fields,models,api


class GastoOperativoMetodoPAgo(models.Model):
    _name = 'gasto.operativo.metodo.pago'

    name = fields.Char(
        string='Método de pago',
    )