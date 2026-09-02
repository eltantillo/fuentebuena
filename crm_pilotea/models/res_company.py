# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    es_pilotea = fields.Boolean(
        string='Es Pilotea',
        help="Si está marcado, el CRM muestra los campos del flujo de "
             "originación de Pilotea cuando esta empresa está entre las "
             "empresas activas.")
