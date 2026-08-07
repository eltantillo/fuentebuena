from odoo import fields,models,api


class InventarioEsquemaAdquisicion(models.Model):
    _name = "inventario.esquema.adquisicion"

    name = fields.Char(
        string="Nombre",
    )