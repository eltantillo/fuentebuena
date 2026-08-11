# -*- coding: utf-8 -*-

from odoo import models, fields

class FbFirmsApreciaFinanciera(models.Model):
    _inherit = 'fb.signature.acknowledged.dependency'
    _name = 'fb.firms.aprecia.financiera'
    _description = 'Firmas de Aprecia Financiera'

