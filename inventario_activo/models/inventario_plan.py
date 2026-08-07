from odoo import fields,models,api


class InventarioPlan(models.Model):
    _name = "inventario.plan"

    name = fields.Char(
        string="Nombre",
    )