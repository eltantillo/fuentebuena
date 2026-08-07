from odoo import fields,models,api


class  InventarioTelefoniaEtapa(models.Model):
    _name = "inventario.telefonia.etapa"

    name = fields.Char(
        string="Nombre"
    )