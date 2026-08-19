# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import api, fields, models
from odoo.fields import Date


class IrUiMenu(models.Model):
    """
        A class to manage the access of ir ui menu.
    """
    _inherit = ["ir.ui.menu", 'mail.thread', 'mail.activity.mixin']

    sh_child_menu = fields.Many2one(
        "ir.ui.menu", string="Hide Menu", tracking=True)

    @api.model
    def get_menus_to_hide(self, company_ids=False):
        """
        Called from javascript to get the list of menu IDs to hide for the current user
        based on the companies selected in the UI.
        """
        # Bypass all restrictions for system administrators
        if self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return []

        # If JS fails to send company_ids, fallback to the current active company.
        if not company_ids:
            company_ids = [self.env.company.id]

        user = self.env.user
        user_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('responsible_user_ids', 'in', user.ids),
            ('sh_restriction_type', '=', 'user'),
            ('company_id', 'in', company_ids),
        ]
        group_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('responsible_group_ids', 'in', user.group_ids.ids),
            ('sh_restriction_type', '=', 'group'),
            ('company_id', 'in', company_ids),
        ]
        access_records = self.env['sh.access.manager'].sudo().search(user_domain) | self.env['sh.access.manager'].sudo().search(group_domain)
        access_records = self.env['sh.access.manager']._sh_filter_by_time(access_records)
        if access_records:
            return access_records.mapped('sh_hide_menu_ids').ids
        return []
