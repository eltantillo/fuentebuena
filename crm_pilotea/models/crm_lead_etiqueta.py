# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class CrmLeadEtiquetaDocumentacion(models.Model):
    _name = 'crm.lead.etiqueta.documentacion'
    _description = 'Etiqueta de estatus de documentación'
    _order = 'name'

    name = fields.Char(string='Etiqueta', required=True)
    color = fields.Integer(string='Color')
    active = fields.Boolean(string='Activo', default=True)

    _name_uniq = models.Constraint(
        'unique(name)',
        'Ya existe una etiqueta de documentación con ese nombre.',
    )


class CrmLeadEtiquetaOferta(models.Model):
    _name = 'crm.lead.etiqueta.oferta'
    _description = 'Etiqueta de oferta presentada'
    _order = 'name'

    name = fields.Char(string='Etiqueta', required=True)
    color = fields.Integer(string='Color')
    active = fields.Boolean(string='Activo', default=True)

    _name_uniq = models.Constraint(
        'unique(name)',
        'Ya existe una etiqueta de oferta con ese nombre.',
    )
