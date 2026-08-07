from odoo import fields,models,api


class InventarioLineaEtapa(models.Model):
    _name = "inventario.linea.etapa"

    name = fields.Char(
        string="Nombre",
    )