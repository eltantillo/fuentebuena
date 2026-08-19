# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

import ast
import json
import logging
from lxml import etree

from odoo import models, SUPERUSER_ID, _, api

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    """
    A class to manage the access of ir ui view.
    """
    _inherit = 'ir.ui.view'

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        """ 
        Include user ID in the cache key. 
        Since Access Management rules modify the view architecture based on the current user,
        we must ensure that the cached version of the view is unique to that user.
        """
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, **options)
        # Include sh_access_management version to force cache invalidation on config changes
        config_version = self.env['ir.config_parameter'].sudo().get_param('sh_access_management.cache_version', '0')
        return key + (self.env.user.id, self.env.company.id, config_version)

    def _postprocess_tag_search(self, node, name_manager, node_info):
        """
        A method to postprocess tag search.
        """
        if self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return

        # Original logic starts here
        postprocessor = getattr(
            super(IrUiView, self), '_postprocess_tag_search', False)
        if postprocessor:
            super(IrUiView, self)._postprocess_tag_search(
                node, name_manager, node_info)
        return None

    def _postprocess_tag_button(self, node, name_manager, node_info):
        """
        A method to postprocess tag button.
        """
        if self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return

        # Original logic starts here
        postprocessor = getattr(
            super(IrUiView, self), '_postprocess_tag_button', False)
        if postprocessor:
            super(IrUiView, self)._postprocess_tag_button(
                node, name_manager, node_info)
        return None

    def _postprocess_tag_page(self, node, name_manager, node_info):
        """
        A method to postprocess tag page.
        """
        if self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return

        # Original logic starts here
        postprocessor = getattr(
            super(IrUiView, self), '_postprocess_tag_page', False)
        if postprocessor:
            super(IrUiView, self)._postprocess_tag_page(
                node, name_manager, node_info)
        return None

    def _postprocess_tag_a(self, node, name_manager, node_info):
        """
        A method to postprocess tag a.
        """
        if self.env.user.has_group('base.group_system') or self.env.user.has_group('sh_access_management.sh_access_management_manager'):
            return

        # Original logic starts here
        _super = getattr(super(IrUiView, self), '_postprocess_tag_a', None)
        if _super:
            _super(node, name_manager, node_info)
        return None

    def _postprocess_tag_field(self, node, name_manager, node_info):
        """
        Odoo 19 Migration: Post-processes field tags to apply access management restrictions.
        """
        user = self.env.user
        model_name = name_manager.model._name
        field_name = node.get('name')

        if not user.has_group('base.group_system') or user.has_group('sh_access_management.sh_access_management_manager') and field_name:
            # Fetch field access rules
            restrictions = self.env['sh.access.manager'].get_model_field_rules(model_name)
            rule = restrictions.get(field_name)

            if rule:
                view_type = node_info.get('view_type')
                is_list = view_type in ['list', 'tree']

                if rule.get('invisible'):
                    node.set('invisible', '1')
                    if is_list:
                        node.set('column_invisible', '1')
                
                if rule.get('readonly'):
                    node.set('readonly', '1')
                    node.set('force_save', '1')
                    if 'attrs' in node.attrib:
                        del node.attrib['attrs']
                
                if rule.get('required'):
                    node.set('required', '1')
                
                # Handle special options like no_open, no_create, no_edit
                if rule.get('no_open') or rule.get('no_create_edit'):
                    try:
                        options_str = node.get('options') or '{}'
                        try:
                            opt = ast.literal_eval(options_str)
                        except (ValueError, SyntaxError):
                            opt = json.loads(options_str.replace("'", '"'))
                        
                        if not isinstance(opt, dict):
                            opt = {}

                        if rule.get('no_open'):
                            opt['no_open'] = True
                        if rule.get('no_create_edit'):
                            opt.update({'no_create': True, 'no_edit': True})
                        
                        node.set('options', str(opt))
                    except Exception:
                        _logger.warning("Failed to update options for field %s", field_name)

        super()._postprocess_tag_field(node, name_manager, node_info)