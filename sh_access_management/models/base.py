# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

import json
import logging
from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import AccessError
from odoo.fields import Date
from odoo.tools import html_escape


class Model(models.AbstractModel):
    """
        A class to manage the access of models.
    """
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        """
            A method to get views with dynamic access management rules applied.
        """
        # Identify all models involved to fetch rules in bulk
        all_models = set()
        if isinstance(views, dict):
            for v_data in views.values():
                if isinstance(v_data, dict) and v_data.get('model'):
                    all_models.add(v_data['model'])
        elif isinstance(views, list):
            for v_data in views:
                if isinstance(v_data, dict) and v_data.get('model'):
                    all_models.add(v_data['model'])
        
        if not all_models:
             all_models.add(self._name)

        user = self.env.user

        common_domain = [
            ('access_manager_id.active_rule', '=', True),
            '|', ('access_manager_id.sh_expiry_date', '=', False), ('access_manager_id.sh_expiry_date', '>=', Date.today()),
            ('access_manager_id.company_id', '=', self.env.company.id),
            ('model_id.model', 'in', list(all_models)),
        ]
        
        user_spec_domain = common_domain + [
            ('access_manager_id.responsible_user_ids', 'in', user.ids),
            ('access_manager_id.sh_restriction_type', '=', 'user')
        ]
        group_spec_domain = common_domain + [
            ('access_manager_id.responsible_group_ids', 'in', user.group_ids.ids),
            ('access_manager_id.sh_restriction_type', '=', 'group')
        ]

        # Fetch restrictions (only filter rules needed before super() call)
        filter_rules = self.env['sh.filter.access'].sudo().search(user_spec_domain) | self.env['sh.filter.access'].sudo().search(group_spec_domain)
        filter_rules = filter_rules.filtered(lambda r: r.access_manager_id._sh_is_within_time_window())

        filter_hide_map = {}
        groupby_hide_map = {}
        for r in filter_rules:
            m = r.model_id.model
            filter_hide_map.setdefault(m, []).extend(r.sh_store_filter_data_ids.mapped('sh_attribute_name'))
            groupby_hide_map.setdefault(m, []).extend(r.sh_store_groupby_data_ids.mapped('sh_attribute_name'))

        modified_context = dict(self.env.context)
        if filter_hide_map.get(self._name) or groupby_hide_map.get(self._name):
            model_filters_to_hide = set(filter_hide_map.get(self._name, []))
            model_groupbys_to_hide = set(groupby_hide_map.get(self._name, []))

            for key in list(modified_context.keys()): # Iterate over a copy to allow modification
                if key.startswith('search_default_'):
                    filter_name = key[len('search_default_'):]
                    if filter_name in model_filters_to_hide or filter_name in model_groupbys_to_hide:
                        del modified_context[key]
        

        res = super(Model, self.with_context(modified_context)).get_views(views, options)

        # Bypass all restrictions for system administrators
        if self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return res

        if not res or not res.get('views'):
            return res

        # Ensure we are working with a mutable copy of the result
        res = dict(res)
        res['views'] = dict(res['views'])

        # Identify all models involved to fetch rules in bulk (refresh all_models from result)
        all_models = set()
        for v_data in res['views'].values():
            if isinstance(v_data, dict) and v_data.get('model'):
                all_models.add(v_data['model'])
        
        if not all_models:
             all_models.add(self._name)

        user = self.env.user
        common_domain = [
            ('access_manager_id.active_rule', '=', True),
            '|', ('access_manager_id.sh_expiry_date', '=', False), ('access_manager_id.sh_expiry_date', '>=', Date.today()),
            ('access_manager_id.company_id', '=', self.env.company.id),
            ('model_id.model', 'in', list(all_models)),
        ]
        
        user_spec_domain = common_domain + [
            ('access_manager_id.responsible_user_ids', 'in', user.ids),
            ('access_manager_id.sh_restriction_type', '=', 'user')
        ]
        group_spec_domain = common_domain + [
            ('access_manager_id.responsible_group_ids', 'in', user.group_ids.ids),
            ('access_manager_id.sh_restriction_type', '=', 'group')
        ]

        # Fetch restrictions
        button_rules = self.env['sh.navbar.buttons.access'].sudo().search(user_spec_domain) | self.env['sh.navbar.buttons.access'].sudo().search(group_spec_domain)
        button_rules = button_rules.filtered(lambda r: r.access_manager_id._sh_is_within_time_window())

        filter_rules = self.env['sh.filter.access'].sudo().search(user_spec_domain) | self.env['sh.filter.access'].sudo().search(group_spec_domain)
        filter_rules = filter_rules.filtered(lambda r: r.access_manager_id._sh_is_within_time_window())

        model_rules = self.env['sh.access.model'].sudo().search(user_spec_domain) | self.env['sh.access.model'].sudo().search(group_spec_domain)
        model_rules = model_rules.filtered(lambda r: r.access_manager_id._sh_is_within_time_window())

        # Global Settings (from access.manager) — needed for sh_readonly
        
        # We still need to check for managers that have NO rules but DO have sh_readonly enabled
        manager_user_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('responsible_user_ids', 'in', user.ids),
            ('sh_restriction_type', '=', 'user'),
            ('company_id', '=', self.env.company.id)
        ]
        manager_group_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('responsible_group_ids', 'in', user.group_ids.ids),
            ('sh_restriction_type', '=', 'group'),
            ('company_id', '=', self.env.company.id)
        ]
        access_managers = self.env['sh.access.manager'].sudo().search(manager_user_domain) | self.env['sh.access.manager'].sudo().search(manager_group_domain)
        access_managers = self.env['sh.access.manager']._sh_filter_by_time(access_managers)
        
        sh_readonly = any(access_managers.mapped('sh_readonly'))

        if not (button_rules or filter_rules or model_rules or sh_readonly):
            return res

        # Map hidden view types per model
        model_hidden_view_types = {}
        # Map model-wise hide_edit flag
        model_hide_edit = {}
        for rule in model_rules:
            m_name = rule.model_id.model
            if m_name not in model_hidden_view_types:
                model_hidden_view_types[m_name] = set()

            vt_names = rule.sudo().view_ids.mapped('technical_name')
            model_hidden_view_types[m_name].update(vt_names)

            # Normalize tree/list: Only if one is explicitly hidden, hide both
            # Odoo 19 technically uses 'list' but 'tree' is still common in metadata
            if 'tree' in vt_names or 'list' in vt_names:
                model_hidden_view_types[m_name].add('tree')
                model_hidden_view_types[m_name].add('list')

            if rule.hide_edit:
                model_hide_edit[m_name] = True

        # Map rules for efficient view processing
        btn_hide_map = {}
        page_hide_map = {}
        link_hide_map = {}
        for r in button_rules:
            m = r.model_id.model
            btn_hide_map.setdefault(m, []).extend(r.sh_store_btn_data_ids)
            page_hide_map.setdefault(m, []).extend(r.sh_store_page_data_ids)
            link_hide_map.setdefault(m, []).extend(r.sh_store_kanban_link_ids)

        filter_hide_map = {}
        groupby_hide_map = {}
        for r in filter_rules:
            m = r.model_id.model
            filter_hide_map.setdefault(m, []).extend(r.sh_store_filter_data_ids.mapped('sh_attribute_name'))
            groupby_hide_map.setdefault(m, []).extend(r.sh_store_groupby_data_ids.mapped('sh_attribute_name'))

        for view_type in list(res['views'].keys()):
            view_data = res['views'][view_type]
            if not isinstance(view_data, dict) or 'arch' not in view_data:
                continue

            view_dict = dict(view_data) # Mutable copy of the view info
            current_model = view_dict.get('model', self._name)
            
            # Use a fresh root for each view
            root = etree.fromstring(view_dict['arch'])
            modified = False

            # Apply global read-only restrictions to view
            if sh_readonly:
                root.set('edit', '0')
                root.set('create', '0')
                root.set('delete', '0')
                root.set('duplicate', '0')
                root.set('import', '0')
                root.set('export', '0')
                modified = True
            elif model_hide_edit.get(current_model):
                # Model-wise hide_edit: make this model read-only (edit only, not create/delete)
                root.set('edit', '0')
                modified = True

            # Check if this entire view type should be hidden for THIS model
            hidden_for_model = model_hidden_view_types.get(current_model, set())
            if view_type in hidden_for_model:
                root.set('invisible', '1')
                modified = True
                del res['views'][view_type]
                continue

            # 2. Buttons
            btns = btn_hide_map.get(current_model, [])
            if btns:
                for b_elem in root.xpath(".//button"):
                    name = b_elem.get('name')
                    string = b_elem.get('string')
                    for r_btn in btns:
                        if r_btn.sh_attribute_name == name:
                            # Match by name and check if string matches (if provided in rule)
                            if not string or _(r_btn.sh_attribute_string) == string:
                                b_elem.set('invisible', '1')
                                # Remove statusbar_visible to ensure 'invisible' attribute is respected in the header
                                if 'statusbar_visible' in b_elem.attrib:
                                    del b_elem.attrib['statusbar_visible']
                                modified = True
                                break

            # 3. Pages
            pages = page_hide_map.get(current_model, [])
            if pages:
                for p_elem in root.xpath(".//page"):
                    p_name = p_elem.get('name')
                    p_string = p_elem.get('string')
                    for r_page in pages:
                        if (p_name and r_page.sh_attribute_name == p_name) or (p_string and _(r_page.sh_attribute_string) == p_string):
                            p_elem.set('invisible', '1')
                            modified = True
                            break

            # 4. Kanban Links
            links = link_hide_map.get(current_model, [])
            if links:
                for a_elem in root.xpath(".//a"):
                    name = a_elem.get('name')
                    tags = a_elem.xpath(".//text()")
                    text = ''.join(tags).strip()
                    for r_link in links:
                        if r_link.sh_attribute_name == name or _(r_link.sh_attribute_string) == text:
                            a_elem.set('invisible', '1')
                            modified = True
                            break

            # 5. Filters
            filters = filter_hide_map.get(current_model, [])
            groupbys = groupby_hide_map.get(current_model, [])
            if filters or groupbys:
                for fltr in root.xpath(".//filter"):
                    fn = fltr.get('name')
                    if fn in filters or fn in groupbys:
                        fltr.set('invisible', '1')
                        modified = True

            if modified:
                view_dict['arch'] = etree.tostring(root, encoding='unicode')
                res['views'][view_type] = view_dict

        # Remove hidden filters/groupbys from search_defaults if they are active by default
        if res.get('search_defaults') and (filter_hide_map.get(self._name) or groupby_hide_map.get(self._name)):
            model_filters_to_hide = set(filter_hide_map.get(self._name, []))
            model_groupbys_to_hide = set(groupby_hide_map.get(self._name, []))

            new_search_defaults = {}
            for key, value in res['search_defaults'].items():
                if key.startswith('search_default_'):
                    filter_name = key[len('search_default_'):]
                    if filter_name not in model_filters_to_hide and filter_name not in model_groupbys_to_hide:
                        new_search_defaults[key] = value
                else:
                    new_search_defaults[key] = value
            res['search_defaults'] = new_search_defaults

        return res

    @api.model
    def get_hidden_filter_data(self, model_name):
        user = self.env.user
        
        # Fetch global restrictions
        global_restrictions_data = self.env['sh.access.manager'].sudo().get_access_restrictions({
            'user_id': user.id,
            'company_id': self.env.company.id
        })

        global_hide_filter = global_restrictions_data.get('model_restrictions', {}).get('global_hide_filter')

        filter_hide_names = []
        groupby_hide_names = []

        # Check if the current model has an explicit model-line override
        # If global_hide_filter is True but the model-line has sh_hide_filter=False,
        # then do NOT hide filters for this specific model
        apply_global_hide = global_hide_filter
        if global_hide_filter:
            # Find access managers applicable to this user
            manager_user_domain = [
                ('active_rule', '=', True),
                '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
                ('responsible_user_ids', 'in', user.ids),
                ('sh_restriction_type', '=', 'user'),
                ('company_id', '=', self.env.company.id),
            ]
            manager_group_domain = [
                ('active_rule', '=', True),
                '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
                ('responsible_group_ids', 'in', user.group_ids.ids),
                ('sh_restriction_type', '=', 'group'),
                ('company_id', '=', self.env.company.id),
            ]
            access_managers = self.env['sh.access.manager'].sudo().search(
                manager_user_domain
            ) | self.env['sh.access.manager'].sudo().search(manager_group_domain)
            access_managers = self.env['sh.access.manager'].sudo()._sh_filter_by_time(access_managers)

            # Check model-line entries for this model
            for manager in access_managers:
                if manager.sh_global_hide_filter:
                    for line in manager.sh_access_model_line:
                        if line.model_id.model == model_name:
                            # Model-line exists for this model
                            if not line.sh_hide_filter:
                                # Model-line says filter should be visible → override global
                                apply_global_hide = False
                            break

        if apply_global_hide:
            store_model_nodes_obj = self.env['sh.store.model.data'].sudo()
            
            model_ir_model = self.env['ir.model'].sudo().search([('model', '=', model_name)], limit=1)
            if model_ir_model:
                dummy_filter_access = self.env['sh.filter.access'].sudo().new({
                    'model_id': model_ir_model.id,
                })
                dummy_filter_access.sudo()._get_filters_groupby() 

            all_filters = store_model_nodes_obj.search([
                ('model_id.model', '=', model_name),
                ('sh_node_option', '=', 'filter')
            ]).mapped('sh_attribute_name')
            all_groupbys = store_model_nodes_obj.search([
                ('model_id.model', '=', model_name),
                ('sh_node_option', '=', 'groupby')
            ]).mapped('sh_attribute_name')
            
            filter_hide_names.extend(all_filters)
            groupby_hide_names.extend(all_groupbys)
        else:
            common_domain = [
                ('access_manager_id.active_rule', '=', True),
                '|', ('access_manager_id.sh_expiry_date', '=', False), ('access_manager_id.sh_expiry_date', '>=', Date.today()),
                ('access_manager_id.company_id', '=', self.env.company.id),
                ('model_id.model', '=', model_name),
            ]
            
            user_spec_domain = common_domain + [
                ('access_manager_id.responsible_user_ids', 'in', user.ids),
                ('access_manager_id.sh_restriction_type', '=', 'user')
            ]
            group_spec_domain = common_domain + [
                ('access_manager_id.responsible_group_ids', 'in', user.group_ids.ids),
                ('access_manager_id.sh_restriction_type', '=', 'group')
            ]

            filter_rules = self.env['sh.filter.access'].sudo().search(user_spec_domain) | self.env['sh.filter.access'].sudo().search(group_spec_domain)

            for r in filter_rules:
                filter_hide_names.extend(r.sh_store_filter_data_ids.mapped('sh_attribute_name'))
                groupby_hide_names.extend(r.sh_store_groupby_data_ids.mapped('sh_attribute_name'))
        
        return {
            'sh_hidden_filter_names': list(set(filter_hide_names)),
            'sh_hidden_groupby_names': list(set(groupby_hide_names)),
        }

    def _sh_check_crud_restriction(self, mode, vals_list=None):
        # Bypass for system/admin user
        if self.env.su or self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return

        # Technical models exempt from access management
        # ... (same as before)
        skip_models = [
            'mail.message', 'mail.notification', 'mail.tracking.value', 'mail.followers', 'mail.activity',
            'mail.message.reaction', 'mail.link.preview', 'mail.message.link.preview',
            'mail.presence', 'res.users.log', 'discuss.channel', 'discuss.channel.member',
            'discuss.gif.favorite', 'mail.guest', 'bus.bus', 'discuss.channel.rtc.session', 
            'discuss.call.history', 'sh.access.manager', 'sh.access.model', 'sh.view.list', 
            'sh.field.access', 'sh.navbar.buttons.access', 'sh.hide.chatter', 'sh.filter.access',
            'sh.conditional.domain'
        ]
        if self._name in skip_models:
            return

        access_rules = self.env['sh.access.model'].check_crud_operation({
            'user_id': self.env.user.id,
            'company_id': self.env.company.id
        })

        if not access_rules:
            return

        # 1. Global Read-Only
        global_rules = access_rules.get('__global__', {})
        if global_rules.get('sh_readonly'):
            raise AccessError(_("🚫 You have read-only access and are not permitted to modify any records."))

        # 2. Model-Specific Restriction
        model_rules = access_rules.get(self._name, {})
        if model_rules:
            if mode == 'create' and model_rules.get('hide_create'):
                raise AccessError(_("🚫 You are not permitted to create records in this model."))
            if mode == 'write' and model_rules.get('hide_edit'):
                raise AccessError(_("🚫 You are not permitted to edit records in this model."))
            if mode == 'unlink' and model_rules.get('hide_delete'):
                raise AccessError(_("🚫 You are not permitted to delete records in this model."))

        rd_rules = model_rules.get('sh_conditional_rules', [])
        if rd_rules:
            from odoo.tools.safe_eval import safe_eval
            from odoo.osv import expression

            mode_field_map = {
                'create': 'hide_create',
                'write': 'hide_write',
                'unlink': 'hide_delete'
            }
            restrict_field = mode_field_map.get(mode)

            for rule in rd_rules:
                # Skip if this mode's CRUD flag is not restricted
                if not rule.get(restrict_field):
                    continue

                domain_str = rule.get('domain')
                has_domain = bool(domain_str)

                if has_domain:
                    # ── Domain set → scope restriction to matching records ──────────────
                    # Applies whether apply_filter=True or False
                    # (user may have set the domain but forgotten to tick "Apply Filter")
                    try:
                        domain_list = safe_eval(domain_str, {})
                        if mode == 'create':
                            # For create: ir_rule.py handles ORM-level blocking at save time.
                            pass
                        elif self.ids:
                            full_domain = expression.AND([[('id', 'in', self.ids)], domain_list])
                            if self.sudo().search_count(full_domain) > 0:
                                raise AccessError(_("🚫 Security Restriction: Matching record(s) are protected by a conditional restriction."))
                    except AccessError:
                        raise
                    except Exception:
                        continue
                else:
                    # ── No domain → apply restriction to ALL records of this model ──────
                    # This is the "apply_filter=False + no domain" case.
                    # Behaves like Model Access tab restriction.
                    if mode == 'create':
                        raise AccessError(_("🚫 You are not permitted to create records in this model."))
                    elif self.ids:
                        raise AccessError(_("🚫 You are not permitted to perform this action on these records."))


    @api.model_create_multi
    def create(self, vals_list):
        self._sh_check_crud_restriction('create', vals_list=vals_list)
        res = super().create(vals_list)
        self.env.registry.clear_cache()
        return res

    def write(self, vals):
        self._sh_check_crud_restriction('write')
        res = super().write(vals)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        self._sh_check_crud_restriction('unlink')
        res = super().unlink()
        self.env.registry.clear_cache()
        return res
