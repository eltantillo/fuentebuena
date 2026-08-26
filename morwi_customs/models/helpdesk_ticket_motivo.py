# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields

from .helpdesk_ticket import TIPO_TICKET_SELECTION


class HelpdeskTicketMotivo(models.Model):
    _name = 'helpdesk.ticket.motivo'
    _description = 'Motivo de ticket'
    _order = 'tipo_ticket, sequence, name'

    name = fields.Char(string='Motivo', required=True)
    tipo_ticket = fields.Selection(selection=TIPO_TICKET_SELECTION, string='Tipo de ticket', required=True)
    sequence = fields.Integer(string='Secuencia', default=10)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_tipo_uniq', 'unique(name, tipo_ticket)',
         'Ya existe un motivo con ese nombre para este tipo de ticket.'),
    ]
