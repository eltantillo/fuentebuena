from odoo import fields,models,api


class InventarioModelo(models.Model):
    _name = "inventario.modelo"

    name = fields.Char(
        string="Nombre"
    )
    fabricante_id = fields.Many2one(
        string="Fabricante",
        comodel_name="inventario.fabricante",
    )
    year = fields.Char(
        string="Año"
    )
    logo = fields.Binary(
        string="Logo",
        compute="_compute_logo",
    )

    def _compute_logo(self):
        for record in self:
            record.logo = record.fabricante_id.logo