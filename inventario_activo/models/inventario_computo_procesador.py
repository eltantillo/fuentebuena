from odoo import fields,models,api


class InventarioComputoProcesador(models.Model):
    _name = "inventario.computo.procesador"


    fabricante_id = fields.Many2one(
        string="Fabricante",
        comodel_name="inventario.fabricante",
    )

    name = fields.Char(
        string="Nombre"
    )