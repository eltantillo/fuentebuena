from odoo import fields, models, api

class FleetTramiteConfig(models.Model):
    _name = 'fleet.tramite.config'

    tipo_tramite_id = fields.Many2one(
        string="Tipo de Tramite",
        comodel_name="fleet.tramite.tipo",
    )
    dependencia = fields.Char(
        string="Dependencia"
    )
    estado = fields.Many2one(
        string="Estado",
        comodel_name="res.country.state",
        domain=[('country_id', '=', 'MX')],
    )
    plaza_id = fields.Many2one(
        string="Plaza",
        comodel_name="fleet.customer.plaza",
    )
    importe = fields.Float(
        string="Importe",
    )
    motivo_pago_id = fields.Many2one(
        string="Motivo de Pago",
        comodel_name="fleet.tramite.motivo.pago",
    )