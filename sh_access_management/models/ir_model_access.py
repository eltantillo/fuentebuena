# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import _, api, models, tools
from odoo.tools import SQL

from .ir_rule import SH_TECHNICAL_MODELS


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @tools.ormcache('self.env.uid', 'self.env.company.id', 'mode')
    def _get_allowed_models(self, mode='read'):
        """
        Extend `_get_allowed_models` to enforce read-only restrictions globally.
        If a user is restricted, their allowed models are limited to technical models only.
        """
        # Admin or system user bypass
        if self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return super()._get_allowed_models(mode)

        # Get rules for CURRENT USER that pass the time-window check
        all_eligible = self.env['sh.access.manager'].sudo().search([
            ('active_rule', '=', True),
            ('sh_readonly', '=', True),
            ('company_id', '=', self.env.company.id),
            '|',
            ('responsible_user_ids', 'in', [self.env.user.id]),
            ('responsible_group_ids', 'in', self.env.user.group_ids.ids),
        ])
        active_ids = self.env['sh.access.manager'].sudo()._sh_filter_by_time(all_eligible).ids

        if not active_ids:
            return super()._get_allowed_models(mode)

        # SQL check for any active read-only restriction for this user or their groups
        query = """
            SELECT COUNT(*) 
            FROM sh_access_manager AS access
            LEFT JOIN sh_access_manager_responsible_user_rel AS u_rel ON access.id = u_rel.sh_access_manager_id
            LEFT JOIN sh_access_manager_responsible_group_rel AS g_rel ON access.id = g_rel.sh_access_manager_id
            WHERE access.id IN %s
              AND (access.sh_expiry_date IS NULL OR access.sh_expiry_date >= CURRENT_DATE)
              AND (
                  (access.sh_restriction_type = 'user' AND u_rel.responsible_user_id = %s)
                  OR 
                  (access.sh_restriction_type = 'group' AND g_rel.responsible_group_id IN %s)
              )
        """
        params = [tuple(active_ids), self.env.user.id, tuple(self.env.user.group_ids.ids) or (0,)]
        self.env.cr.execute(query, params)
        restricted_count = self.env.cr.fetchone()[0]

        allowed = super()._get_allowed_models(mode)
        if restricted_count > 0 and mode in ['write', 'create', 'unlink']:
            # Technical models allowed even in global readonly mode
            # In Odoo 19, this returns a frozenset.
            return frozenset(allowed & set(SH_TECHNICAL_MODELS))

        return allowed

    # Custom error override for readonly restriction
    def _make_access_error(self, model: str, mode: str):
        """
        A method to make access error.
        """
        # Bypass for admin/system user
        if self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return super()._make_access_error(model, mode)

        # Technical models exempt from global read-only
        if model in SH_TECHNICAL_MODELS:
            return super()._make_access_error(model, mode)

        # Get rules for CURRENT USER that pass the time-window check
        all_eligible = self.env['sh.access.manager'].sudo().search([
            ('active_rule', '=', True),
            ('sh_readonly', '=', True),
            ('company_id', '=', self.env.company.id),
            '|',
            ('responsible_user_ids', 'in', [self.env.user.id]),
            ('responsible_group_ids', 'in', self.env.user.group_ids.ids),
        ])
        active_ids = self.env['sh.access.manager'].sudo()._sh_filter_by_time(all_eligible).ids

        if not active_ids:
            return super()._make_access_error(model, mode)

        self.env.cr.execute("""
            SELECT COUNT(*) 
            FROM sh_access_manager AS access
            LEFT JOIN sh_access_manager_responsible_user_rel AS u_rel ON access.id = u_rel.sh_access_manager_id
            LEFT JOIN sh_access_manager_responsible_group_rel AS g_rel ON access.id = g_rel.sh_access_manager_id
            WHERE access.id IN %s
              AND (access.sh_expiry_date IS NULL OR access.sh_expiry_date >= CURRENT_DATE)
              AND (
                  (access.sh_restriction_type = 'user' AND u_rel.responsible_user_id = %s)
                  OR 
                  (access.sh_restriction_type = 'group' AND g_rel.responsible_group_id IN %s)
              )
        """, [tuple(active_ids), self.env.user.id, tuple(self.env.user.group_ids.ids) or (0,)])

        restricted_count = self.env.cr.fetchone()[0]

        if restricted_count > 0 and mode in ['write', 'create', 'unlink']:
            from odoo.exceptions import AccessError
            return AccessError(_('🚫 You have read-only access and are not permitted to modify any records.'))

        return super()._make_access_error(model, mode)