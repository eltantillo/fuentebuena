from odoo import fields, models, api

class FleetCompraEtapa(models.Model):
    _name = "fleet.compra.etapa"
    _description = "Etapa de compra"

    name = fields.Char(
        string="Nombre"
    )