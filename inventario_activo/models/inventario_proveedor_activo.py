from odoo import fields,models,api

class InventarioProveedorActivo(models.Model):
    _name = "inventario.proveedor.activo"

    name = fields.Char(
        string="Nombre"
    )
    logo = fields.Binary(
        string="Logo",
    )