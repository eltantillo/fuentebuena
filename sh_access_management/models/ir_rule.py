# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import api, models
from odoo.fields import Domain
from odoo.tools.safe_eval import safe_eval


class IrRule(models.Model):
    """
    A class to manage the access of ir rule.
    """
    _inherit = 'ir.rule'

    @api.model
    def _compute_domain(self, model_name: str, mode: str = "read") -> Domain:
        """
        Improved Domain Engine:
        - Presence of a rule line = User SCOPED to those records (Whitelist for Read).
        - 'Read Only' box (sh_conditional_readonly): If Checked, blocks modify actions for matching records.
        - 'Create/Update/Delete' boxes: If Checked, blocks those specific modify actions.
        """
        model = self.env[model_name]
        
        # parent models
        global_domains: list[Domain] = []
        for parent_model_name, parent_field_name in model._inherits.items():
            if not model._fields[parent_field_name].store:
                continue
            if domain := self._compute_domain(parent_model_name, mode):
                global_domains.append(Domain(parent_field_name, 'any', domain))

        rules = self._get_rules(model_name, mode=mode)
        if rules:
            eval_context = self._eval_context()
            user_groups = self.env.user.all_group_ids
            group_domains: list[Domain] = []
            for rule in rules.sudo():
                if rule.groups and not (rule.groups & user_groups):
                    continue
                dom = Domain(safe_eval(rule.domain_force, eval_context)) if rule.domain_force else Domain.TRUE
                if rule.groups:
                    group_domains.append(dom)
                else:
                    global_domains.append(dom)
            if group_domains:
                global_domains.append(Domain.OR(group_domains))

        # Access Management Check
        if not (self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager')):
            skip_models = [
                'mail.message', 'mail.notification', 'mail.tracking.value', 'mail.followers', 'mail.activity',
                'mail.message.reaction', 'mail.link.preview', 'mail.message.link.preview',
                'mail.presence', 'res.users.log', 'discuss.channel', 'discuss.channel.member',
                'discuss.gif.favorite', 'mail.guest', 'bus.bus', 'discuss.channel.rtc.session', 
                'discuss.call.history', 'sh.access.manager', 'sh.access.model', 'sh.view.list', 
                'sh.field.access', 'sh.navbar.buttons.access', 'sh.hide.chatter', 'sh.filter.access',
                'sh.store.model.data', 'sh.conditional.domain'
            ]
            is_technical = model_name in skip_models
            
            if not is_technical and mode in ['write', 'create', 'unlink']:
                all_eligible = self.env['sh.access.manager'].sudo().search([
                    ('active_rule', '=', True), ('sh_readonly', '=', True),
                    '|', ('company_id', '=', False), ('company_id', 'in', self.env.companies.ids),
                ])
                active_ids = self.env['sh.access.manager'].sudo()._sh_filter_by_time(all_eligible).ids
                if active_ids:
                    sql_params = [tuple(active_ids), tuple(self.env.companies.ids) or (0,), self.env.user.id, tuple(self.env.user.all_group_ids.ids) or (0,)]
                    self.env.cr.execute("""
                        SELECT COUNT(*) FROM sh_access_manager AS access
                        LEFT JOIN sh_access_manager_responsible_user_rel AS u_rel ON access.id = u_rel.sh_access_manager_id
                        LEFT JOIN sh_access_manager_responsible_group_rel AS g_rel ON access.id = g_rel.sh_access_manager_id
                        WHERE access.id IN %s AND (access.sh_expiry_date IS NULL OR access.sh_expiry_date >= CURRENT_DATE)
                          AND (access.company_id IS NULL OR access.company_id IN %s)
                          AND ( (access.sh_restriction_type = 'user' AND u_rel.responsible_user_id = %s)
                                OR (access.sh_restriction_type = 'group' AND g_rel.responsible_group_id IN %s) )
                    """, sql_params)
                    if self.env.cr.fetchone()[0] > 0:
                        global_domains.append(Domain([('id', '=', 0)]))

            # ── Record Domain Logic ───────────────────────────────────────────────
            if not is_technical:
                all_conditional_rules = self.env['sh.conditional.domain'].sudo().search([
                    ('sh_model_id.model', '=', model_name),
                    ('sh_access_manager_id.active_rule', '=', True),
                    '|', ('sh_access_manager_id.company_id', '=', False),
                         ('sh_access_manager_id.company_id', 'in', self.env.companies.ids),
                ])
                
                if all_conditional_rules:
                    valid_time_rules = all_conditional_rules.filtered(lambda r: r.sh_access_manager_id._sh_is_within_time_window())
                    active_mgr_ids = valid_time_rules.mapped('sh_access_manager_id').ids
                    
                    if active_mgr_ids:
                        sql_params = [tuple(active_mgr_ids), tuple(self.env.companies.ids) or (0,), self.env.user.id, tuple(self.env.user.all_group_ids.ids) or (0,)]
                        self.env.cr.execute("""
                            SELECT DISTINCT access.id FROM sh_access_manager AS access
                            LEFT JOIN sh_access_manager_responsible_user_rel AS u_rel ON access.id = u_rel.sh_access_manager_id
                            LEFT JOIN sh_access_manager_responsible_group_rel AS g_rel ON access.id = g_rel.sh_access_manager_id
                            WHERE access.id IN %s AND (access.sh_expiry_date IS NULL OR access.sh_expiry_date >= CURRENT_DATE)
                              AND (access.company_id IS NULL OR access.company_id IN %s)
                              AND ( (access.sh_restriction_type = 'user' AND u_rel.responsible_user_id = %s)
                                    OR (access.sh_restriction_type = 'group' AND g_rel.responsible_group_id IN %s) )
                        """, sql_params)
                        app_mgr_ids = [row[0] for row in self.env.cr.fetchall()]
                        
                        if app_mgr_ids:
                            mode_field_map = {'write': 'sh_conditional_update', 'create': 'sh_conditional_create', 'unlink': 'sh_conditional_delete'}
                            curr_restrict_field = mode_field_map.get(mode)
                            
                            white_domains = []
                            black_domains = []
                            
                            for rule in valid_time_rules:
                                if rule.sh_access_manager_id.id not in app_mgr_ids:
                                    continue
                                
                                # Process the domain
                                dom_list = safe_eval(rule.sh_conditional_domain, self._eval_context()) if rule.sh_conditional_domain else []
                                if not dom_list and not rule.sh_conditional_domain:
                                    dom_list = [(1, '=', 1)]
                                
                                # ALWAYS add to Whitelist for Read Mode (Scopes visibility)
                                if mode == 'read':
                                    white_domains.append(Domain(dom_list))
                                
                                # Add to Blacklist if action is restricted
                                # (Restricted by 'Read Only' box OR specific CRUD box)
                                is_blocked = False
                                if rule.sh_conditional_readonly:
                                    # Read Only box blocks editing and deleting
                                    is_blocked = True
                                elif curr_restrict_field and rule[curr_restrict_field]:
                                    # Specific Create/Update/Delete box blocks that specific action
                                    is_blocked = True
                                
                                if is_blocked and mode != 'read':
                                    black_domains.append(Domain(dom_list))

                            if mode == 'read' and white_domains:
                                # Scope the user to these records ONLY
                                # NOTE: Read Only checkbox DOES NOT hide records anymore, it just blocks modify.
                                final_read = Domain.OR(white_domains)
                                global_domains.append(final_read)

                            elif mode != 'read' and black_domains:
                                # Block modification to matching records
                                final_black = Domain.OR(black_domains)
                                global_domains.append(~final_black)


        final_res = Domain.AND(global_domains).optimize(model)
        return final_res
