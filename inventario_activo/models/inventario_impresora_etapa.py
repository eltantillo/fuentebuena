from odoo import fields,models,api


class InventarioImpresoraEtapa(models.Model):
    _name = "inventario.impresora.etapa"

    name = fields.Char(
        string="Nombre"
    )