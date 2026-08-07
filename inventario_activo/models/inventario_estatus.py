from odoo import fields,models,api


class InventarioEstatus(models.Model):
    _name = "inventario.estatus"

    name = fields.Char(
        string="Nombre",
    )