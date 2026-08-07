from odoo import models, fields, api


class FleetPolizaTipoValor(models.Model):
    _name = 'fleet.poliza.tipo.valor'
    _description = 'Tipos de polizas de seguro'

    name = fields.Char(string='Tipo de poliza')
    active = fields.Boolean('Active', default=True, tracking=True)