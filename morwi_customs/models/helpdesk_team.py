# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class HelpdeskTeam(models.Model):

    _inherit = 'helpdesk.team'

    user_id = fields.Many2one(
        comodel_name='res.users', string='Team Leader',
        domain=lambda self: f"[('all_group_ids', 'in', {self.env.ref('helpdesk.group_helpdesk_user').id}), ('company_ids', 'in', [company_id])]")

    auto_assignment = fields.Boolean(default=True)
    assign_method = fields.Selection(default='balanced')
