from odoo import fields, models, api

class FleetCompraCondicion(models.Model):
    _name = "fleet.compra.condicion"
    _description = "Condiciones de compra"

    name = fields.Char(
        string="Nombre"
    )