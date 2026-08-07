from odoo import fields,models,api

class InventarioImpresoraConectividad(models.Model):
    _name = "inventario.impresora.conectividad"

    name = fields.Char(
        string="Nombre",
    )