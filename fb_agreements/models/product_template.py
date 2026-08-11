# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Checkbox para habilitar el producto en el módulo de convenios
    fb_available_in_agreements = fields.Boolean(
        string='Aprecia',
        default=False, copy=False,
        help='Si está marcado, este producto aparecerá disponible para seleccionarse dentro de los convenios de aprecia')