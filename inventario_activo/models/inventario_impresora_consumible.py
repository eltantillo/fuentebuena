from odoo import fields,models,api

class InventarioImpresoraConsumible(models.Model):
    _name = "inventario.impresora.consumible"

    name = fields.Char(
        string="Nombre"
    )