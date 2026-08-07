from odoo import fields, models, api

class ProveedorTipo(models.Model):
    _name = 'proveedor.tipo'
    _description = 'Tipo de Proveedor'

    name = fields.Char(
        string='Tipo de Proveedor'
    )