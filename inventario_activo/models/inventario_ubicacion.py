from odoo import fields,models,api

class InventarioUbicacion(models.Model):
    _name = "inventario.ubicacion"

    name = fields.Char(
        string="Nombre",
    )