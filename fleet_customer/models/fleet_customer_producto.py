from odoo import models, fields, api

class FleetCustomerProducto(models.Model):
    _name = "fleet.customer.producto"
    _description = "Módulo personalizado para registrar los productos para los vehículos"

    name = fields.Char(
        string='Nombre de producto',
    )
    prefijo = fields.Char(
        string='Prefijo',
    )
    flotilla_id = fields.Many2one(
        string='Flotilla',
        comodel_name="fleet.customer.flotilla",
    )