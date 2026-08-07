from odoo import fields,models,api


class InventarioFabricante(models.Model):
    _name = "inventario.fabricante"

    name = fields.Char(
        string="Nombre"
    )
    logo = fields.Binary(
        string="Logo",
    )
