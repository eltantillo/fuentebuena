from odoo import models,fields,api

class FacturaUnspscCategoria(models.Model):
    _name = 'product.unspsc.categoria'
    _rec_name = 'categoria_id'
    _description = 'Modelo para añadir categoria a los productos unspsc'

    categoria_id = fields.Many2one(
        comodel_name='product.product',
        string='Categoria',
    )
    products_ids = fields.Many2many(
        comodel_name='product.unspsc.code',
        string='Productos unspsc',
    )

    @api.model
    def create(self, vals):
        for code in self.products_ids:
            code.categoria_id = self.categoria_id
        res = super().create(vals)
        return res