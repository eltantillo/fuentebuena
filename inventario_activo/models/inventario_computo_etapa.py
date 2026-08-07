from odoo import fields,models,api


class InventarioComputoEtapa(models.Model):
    _name = "inventario.computo.etapa"

    name = fields.Char(
        string="Nombre",
    )
