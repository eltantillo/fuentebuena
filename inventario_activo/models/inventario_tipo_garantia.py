from odoo import fields,models,api

class InventarioTipoGarantia(models.Model):
    _name = "inventario.tipo.garantia"

    name = fields.Char(
        string="Nombre",
    )