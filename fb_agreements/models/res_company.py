# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    fb_aprecia = fields.Boolean(
        string='Aprecia',
        default=False, copy=False,
        help='Si está marcado, la empresa es Aprecia')