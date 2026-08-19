# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import models
from odoo.fields import Date

class IRactioonsActWindow(models.Model):
    """
        A class to manage the access of ir actions act window.
    """
    _inherit = 'ir.actions.act_window'

    def read(self, flds=None, load='_classic_read'):
        """
            A method to read the records.
        """
        # Bypass all restrictions for system administrators
        if self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return super().read(flds, load=load)

        results = super().read(flds, load=load)
        user = self.env.user
        Manager = self.env['sh.access.manager'].sudo()
        
        # Cache access managers for the current user
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
        all_access_managers = Manager.search(user_domain) | Manager.search(group_domain)
        # Apply time-window filter
        all_access_managers = Manager.sudo()._sh_filter_by_time(all_access_managers)

        if not all_access_managers:
            return results

        for result in results:
            res_model = result.get('res_model')
            if not res_model and 'id' in result:
                res_model = self.sudo().browse(result['id']).res_model

            if res_model:
                # Find hidden views for this specific model from the already fetched access managers
                view_list = []
                for manager in all_access_managers:
                    for model_access in manager.sh_access_model_line:
                        if model_access.sudo().model_id.model == res_model:
                            view_list.extend(model_access.sudo().view_ids.mapped('technical_name'))
                
                if not view_list:
                    continue

                # Filter view_mode and binding_view_types
                for field_name in ['view_mode', 'binding_view_types']:
                    if field_name in result and result[field_name]:
                        current_val = result[field_name]
                        current_views = [v.strip() for v in current_val.split(',')]
                        
                        new_allowed_views = []
                        for view_type in current_views:
                            is_hidden = False
                            if view_type in ['tree', 'list']:
                                if 'tree' in view_list or 'list' in view_list:
                                    is_hidden = True
                            elif view_type in view_list:
                                is_hidden = True
                            
                            if not is_hidden:
                                new_allowed_views.append(view_type)
                        result[field_name] = ','.join(new_allowed_views)

                # Handle views tuple list if present (synced with view_mode)
                if 'views' in result and result['views'] and 'view_mode' in result:
                    final_view_modes = result['view_mode'].split(',')
                    new_views = [v for v in result['views'] if isinstance(v, (list, tuple)) and v[1] in final_view_modes]
                    result['views'] = new_views

        return results
