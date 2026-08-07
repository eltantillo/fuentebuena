from odoo import fields, models, api

class FleetCompraCategoria(models.Model):
    _name = "fleet.compra.categoria"
    _descripcion = "Categorías de compras"

    name = fields.Char(
        string = "Nombre categoría"
    )