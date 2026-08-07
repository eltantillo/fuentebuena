from odoo import fields,models,api


class  InventarioRegion(models.Model):
    _name = "inventario.region"

    name = fields.Char(
        string="Nombre"
    )