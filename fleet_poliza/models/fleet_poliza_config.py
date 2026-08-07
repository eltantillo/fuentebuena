from odoo import fields,models,api


class FleetPolizaConfig(models.Model):

    _name = 'fleet.poliza.config'

    tipo_poliza_id = fields.Many2one(
        string='Tipo',
        comodel_name='fleet.poliza.tipo',
    )
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor',
        domain=[('supplier_rank', '>', 0)]
    )
    tipo_cobertura_id = fields.Many2one(
        comodel_name='fleet.poliza.tipo.cobertura',
        string='Tipo de cobertura'
    )
    tipo_valor_id = fields.Many2one(
        comodel_name='fleet.poliza.tipo.valor',
        string='Tipo de valor'
    )
    prima_neta = fields.Float(
        string='Prima neta',
        tracking=True
    )
    gasto_expedicion = fields.Float(
        string='Gastos de expedición',
        tracking=True
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
    )