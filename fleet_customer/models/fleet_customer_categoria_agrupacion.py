from odoo import models, fields

class FleetCustomerCategoriaAgrupacion(models.Model):
    _name = "fleet.customer.categoria.agrupacion"
    _description = "Módulo personalizado para registrar las categorias de agrupaciones para los vehículos"

    name = fields.Char(
        string='Nombre de categoria',
    )