# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from collections import defaultdict
from types import MappingProxyType as frozendict

from odoo import _, api, fields, models, tools
from odoo.fields import Date
from odoo.exceptions import AccessError, MissingError


class ReportActions(models.Model):
    """
        A class to manage the access of report actions.
    """
    _inherit = 'ir.actions.actions'

    @tools.ormcache('model_name', 'self.env.lang', 'self.env.uid', 'self.env.company.id')
    def _get_bindings(self, model_name, debug=False):
        """ Retrieve the list of actions bound to the given model.

        :return: a dict mapping binding types to a list of dict describing
                 actions, where the latter is given by calling the method
                 ``read`` on the action record.
        """
        # Get the original, undecorated _get_bindings method from the parent class
        # This bypasses the ormcache decorator on the super method
        original_get_bindings = super(ReportActions, self)._get_bindings.__wrapped__

        # If system administrator, return the unfiltered result from the original method
        if self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return original_get_bindings(self, model_name)

        cr = self.env.cr
        ir_model_access = self.env['ir.model.access']

        result = defaultdict(list)
        user_groups = self.env.user.group_ids
        if not debug:
            user_groups -= self.env.ref('base.group_no_one')

        self.env.flush_all()
        cr.execute("""
            SELECT a.id, a.type, a.binding_type
              FROM ir_actions a
              JOIN ir_model m ON a.binding_model_id = m.id
             WHERE m.model = %s
          ORDER BY a.id
        """, [model_name])

        for action_id, action_model, binding_type in cr.fetchall():
            try:
                action = self.env[action_model].sudo().browse(action_id)
                action_groups = getattr(action, 'group_ids', ())
                action_model_name = getattr(action, 'res_model', False)
                if action_groups and not action_groups & user_groups:
                    continue
                if action_model_name and not ir_model_access.sudo().check(
                        action_model_name, mode='read', raise_exception=False):
                    continue
                fields_to_read = ['name', 'binding_view_types']
                if 'sequence' in action._fields:
                    fields_to_read.append('sequence')
                result[binding_type].append(action.read(fields_to_read)[0])
            except (AccessError, MissingError):
                continue

        if result.get('action'):
            result['action'] = sorted(
                result['action'], key=lambda vals: vals.get('sequence', 0))

        allowed_reports = result.get('report', [])
        allowed_actions = result.get('action', [])

        if allowed_actions or allowed_reports:
            user = self.env.user
            user_domain = [
                ('active_rule', '=', True),
                '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
                ('responsible_user_ids', 'in', user.ids),
                ('sh_restriction_type', '=', 'user'),
                ('company_id', '=', self.env.company.id)
            ]
            group_domain = [
                ('active_rule', '=', True),
                '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
                ('responsible_group_ids', 'in', user.group_ids.ids),
                ('sh_restriction_type', '=', 'group'),
                ('company_id', '=', self.env.company.id)
            ]
            find_access = self.env['sh.access.manager'].sudo().search(user_domain) | self.env['sh.access.manager'].sudo().search(group_domain)
            # Apply time-window filter
            find_access = self.env['sh.access.manager'].sudo()._sh_filter_by_time(find_access)

            temp_report = []
            temp_action = []

            # Global hide
            hide_all_actions = find_access.filtered(
                lambda r: r.sh_global_hide_action_button)
            hide_all_reports = find_access.filtered(
                lambda r: r.sh_global_hide_print_button)

            # Skip model-level filtering if globally hidden
            if not hide_all_actions or not hide_all_reports:
                for model_access in find_access.sh_access_model_line:
                    if model_access.model_id.model == model_name:
                        if not hide_all_actions and model_access.sh_hide_action:
                            hide_all_actions = True
                        if not hide_all_reports and model_access.sh_hide_print:
                            hide_all_reports = True

                        if not hide_all_reports:
                            for allowed in allowed_reports:
                                for report in model_access.report_ids:
                                    if allowed['id'] == report.id:
                                        temp_report.append(report.id)

                        if not hide_all_actions:
                            for allowed_action in allowed_actions:
                                if allowed_action['id'] == model_access.action_id.id:
                                    temp_action.append(
                                        model_access.action_id.id)

            # Conditional domain rules: if any rule for this model has
            # sh_conditional_action or sh_conditional_print, apply the same hiding
            if not hide_all_actions or not hide_all_reports:
                conditional_rules = self.env['sh.conditional.domain'].sudo().search([
                    ('sh_access_manager_id', 'in', find_access.ids),
                    ('sh_model_name', '=', model_name),
                ])
                for rd in conditional_rules:
                    if not hide_all_actions and rd.sh_conditional_action:
                        hide_all_actions = True
                    if not hide_all_reports and rd.sh_conditional_print:
                        hide_all_reports = True
                    if hide_all_actions and hide_all_reports:
                        break

            # Final filtering
            if hide_all_actions:
                result['action'] = []
            else:
                result['action'] = [action_dic for action_dic in allowed_actions
                                    if action_dic['id'] not in temp_action]

            if hide_all_reports:
                result['report'] = []
            else:
                result['report'] = [item_dic for item_dic in allowed_reports
                                    if item_dic['id'] not in temp_report]

        return frozendict(result)
