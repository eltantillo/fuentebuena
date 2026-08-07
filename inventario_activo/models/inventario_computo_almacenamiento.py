from odoo import fields,models,api

class InventarioComputoAlmacenamiento(models.Model):
    _name = "inventario.computo.almacenamiento"

    name = fields.Char(
        string="Nombre"
    )