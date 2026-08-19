# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

import re
from lxml import etree
from markupsafe import Markup

from odoo import fields, models, api, _
from odoo.tools import html_escape


class HideViewNodes(models.Model):
    """
        A class to manage the access of navbar buttons.
    """
    _name = 'sh.navbar.buttons.access'
    _description = 'Hide Navbar And Buttos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    model_id = fields.Many2one(
        'ir.model', string='Model', index=True, required=True,
        ondelete='cascade', tracking=True,
        domain="[('model', '!=', 'sh.access.manager')]")

    model_name = fields.Char(
        string='Model Name', related='model_id.model',
        readonly=True, store=True, tracking=True)

    sh_store_btn_data_ids = fields.Many2many(
        'sh.store.model.data',
        'sh_btn_hide_view_nodes_store_model_nodes_rel',
        'sh_hide_id', 'sh_store_id',
        string='Hide Button',
        domain="[('sh_node_option','=','button')]",
        tracking=True)

    sh_store_page_data_ids = fields.Many2many(
        'sh.store.model.data',
        'sh_page_hide_view_nodes_store_model_nodes_rel',
        'sh_hide_id', 'sh_store_id',
        string='Hide Tab/Page',
        domain="[('sh_node_option','=','page')]",
        tracking=True)

    sh_store_kanban_link_ids = fields.Many2many(
        'sh.store.model.data',
        'sh_kanban_link_hide_view_nodes_store_model_nodes_rel',
        'sh_hide_id', 'sh_store_id',
        string='Hide Kanban Link',
        domain="[('model_id','=',model_id),('sh_node_option','=','link')]",
        tracking=True
    )

    access_manager_id = fields.Many2one(
        'sh.access.manager', string='Access Management', tracking=True)

    def _store_btn_data(self, btn, smart_button=False, smart_button_string=False):
        """
            A method to store button data.
        """
        # string_value is used in case of kanban view button store,
        string_value = self.env.context.get('string_value', False)

        store_model_button_obj = self.env['sh.store.model.data']
        name = btn.get('string') or string_value
        if smart_button:
            name = smart_button_string + ' - (Smart Button)'
        store_model_button_obj.create({
            'model_id': self.model_id.id,
            'sh_node_option': 'button',
            'sh_attribute_name': btn.get('name'),
            'sh_attribute_string': name,
            'sh_button_type': btn.get('type'),
            'sh_is_smart_button': smart_button,
        })

    def _get_smart_btn_string(self, btn_list, button_type=False):
        """
            A method to get smart button string.
        """
        store_model_button_obj = self.env['sh.store.model.data'].sudo()
        for btn in btn_list:
            button_xml_name = btn.get('name')
            if not button_xml_name: # A button must have a name to be useful
                continue

            display_string = ""
            # Prioritize string from nested <field>
            field_node = btn.find('div/field') or btn.find('field')
            if field_node is not None and field_node.get('string'):
                display_string = field_node.get('string')
            
            # Fallback to string attribute of the button itself
            if not display_string:
                display_string = btn.get('string')

            # Fallback to all text content within the button
            if not display_string:
                display_string = ' '.join(btn.xpath(".//text()")).strip()
            
            # If still no display string, skip this button
            if not display_string:
                continue

            # Normalize whitespace and append "(Smart Button)"
            display_string = re.sub(r'\s+', ' ', display_string).strip()
            display_string += ' - (Smart Button)'

            # Construct a robust domain for searching existing records
            domain = [
                ('model_id', '=', self.model_id.id),
                ('sh_node_option', '=', 'button'),
                ('sh_attribute_name', '=', button_xml_name), # Use the XML 'name' attribute for uniqueness
                ('sh_is_smart_button', '=', True),
            ]
            
            smart_button_id = store_model_button_obj.search(domain, limit=1)
            
            if not smart_button_id:
                # Create new record if not found
                store_model_button_obj.create({
                    'model_id': self.model_id.id,
                    'sh_node_option': 'button',
                    'sh_attribute_name': button_xml_name,
                    'sh_attribute_string': display_string,
                    'sh_button_type': btn.get('type'),
                    'sh_is_smart_button': True,
                })
            else:
                # Update existing record if found (e.g., ensure sh_is_smart_button is True and update string if needed)
                smart_button_id.write({
                    'sh_is_smart_button': True,
                    'sh_attribute_string': display_string # Update string in case it changed
                })

    def _get_button_and_page_data(self, doc, view, store_model_nodes_obj):
        """
            A method to get button and page data.
        """
        object_link = doc.xpath("//a")
        for btn in object_link:
            if btn.text and '\n' not in btn.text and 'type' in btn.attrib.keys() and \
                btn.attrib['type'] and 'name' in btn.attrib.keys() and \
                    btn.attrib['name']:
                domain = [('sh_button_type', '=', btn.get('type')),
                          ('sh_attribute_string', '=', btn.text),
                          ('sh_attribute_name', '=', btn.get('name')),
                          ('model_id', '=', self.model_id.id),
                          ('sh_node_option', '=', 'link')]
                if not store_model_nodes_obj.search(domain):
                    store_model_nodes_obj.create({
                        'model_id': self.model_id.id,
                        'sh_node_option': 'link',
                        'sh_attribute_name': btn.get('name'),
                        'sh_attribute_string': btn.text,
                        'sh_button_type': btn.get('type'),
                    })
        # Object type button
        object_button = doc.xpath("//button[@type='object']")
        for btn in object_button:
            string_value = btn.get('string')
            if view == 'kanban' and not string_value:
                try:
                    string_value = btn.text if not btn.text.startswith(
                        '\n') else False
                except AttributeError:
                    # This is to handle cases where text is not present
                    pass
            if string_value: # Normalize string_value if it exists
                string_value = re.sub(r'\s+', ' ', string_value).strip()
            if btn.get('name') and string_value:
                domain = [('sh_button_type', '=', btn.get('type')),
                          ('sh_attribute_string', '=', string_value),
                          ('sh_attribute_name', '=', btn.get('name')),
                          ('model_id', '=', self.model_id.id),
                          ('sh_node_option', '=', 'button')]
                if not store_model_nodes_obj.search(domain):
                    self.with_context(
                        string_value=string_value)._store_btn_data(btn)
        # Action type button
        action_button = doc.xpath("//button[@type='action']")
        for btn in action_button:
            string_value = btn.get('string')
            if view == 'kanban' and not string_value:
                try:
                    string_value = btn.text if not btn.text.startswith(
                        '\n') else False
                except AttributeError:
                    # This is to handle cases where text is not present
                    pass
            if string_value: # Normalize string_value if it exists
                string_value = re.sub(r'\s+', ' ', string_value).strip()
            if btn.get('name') and string_value:
                domain = [('sh_button_type', '=', btn.get('type')),
                          ('sh_attribute_string', '=', string_value),
                          ('sh_attribute_name', '=', btn.get('name')),
                          ('model_id', '=', self.model_id.id),
                          ('sh_node_option', '=', 'button')]
                if not store_model_nodes_obj.search(domain):
                    self.with_context(
                        string_value=string_value)._store_btn_data(btn)

    def _extract_kanban_links_and_buttons(self, res, store_model_nodes_obj):
        """
            A method to extract kanban links and buttons.
        """
        arch_raw = res.get('arch', '')
        try:
            doc = etree.XML(arch_raw)
        except Exception:
            return
        # Extract all <a> with type + name
        a_nodes = doc.xpath(".//a[@type='object' or @type='action']")
        for node in a_nodes:
            name = node.get('name')
            if not name:
                continue
            string_val = ''.join(node.itertext()).strip()
            if string_val:
                string_val = re.sub(r'\s+', ' ', string_val).strip() # Normalize string_val
                domain = [
                    ('model_id', '=', self.model_id.id),
                    ('sh_node_option', '=', 'kanban_link'),
                    ('sh_attribute_name', '=', name),
                    ('sh_attribute_string', '=', string_val)
                ]
                if not store_model_nodes_obj.search(domain):
                    store_model_nodes_obj.create({
                        'model_id': self.model_id.id,
                        'sh_node_option': 'kanban_link',
                        'sh_attribute_name': name,
                        'sh_attribute_string': string_val
                    })
        # Extract all <button> with type + name
        button_nodes = doc.xpath(
            ".//button[@type='object' or @type='action']")
        for node in button_nodes:
            name = node.get('name')
            if not name:
                continue
            string_val = node.get('string') or ''.join(
                node.itertext()).strip()
            if string_val:
                string_val = re.sub(r'\s+', ' ', string_val).strip() # Normalize string_val
                domain = [
                    ('model_id', '=', self.model_id.id),
                    ('sh_node_option', '=', 'button'),
                    ('sh_attribute_name', '=', name),
                    ('sh_attribute_string', '=', string_val)
                ]
                if not store_model_nodes_obj.search(domain):
                    store_model_nodes_obj.create({
                        'model_id': self.model_id.id,
                        'sh_node_option': 'button',
                        'sh_attribute_name': name,
                        'sh_attribute_string': string_val
                    })

    def _extract_smart_buttons_and_tabs(self, doc, store_model_nodes_obj):
        """
            A method to extract smart buttons and tabs.
        """
        if doc.xpath("//form"):
            # Smart Buttons Extraction
            smt_button_division = doc.xpath(
                "//div[@class='oe_button_box']")
            if smt_button_division:
                smt_button_division_element = smt_button_division[0] # Keep original element
                smt_button_division_str = etree.tostring(smt_button_division_element, pretty_print=True, encoding='unicode')

                smt_button_division_parsed = etree.XML(smt_button_division_str) # Parse the string
                
                smt_object_button = smt_button_division_parsed.xpath( # Use the parsed element
                    ".//button[@type='object']")
                self._get_smart_btn_string(
                    smt_object_button, button_type='object')
                smt_action_button = smt_button_division_parsed.xpath( # Use the parsed element
                    ".//button[@type='action']")
                self._get_smart_btn_string(
                    smt_action_button, button_type='action')
            # Tab Extraction
            page_list = doc.xpath("//page")
            if page_list:
                for page in page_list:
                    if page.get('string'):
                        domain = [('sh_attribute_string', '=', page.get('string')),
                                  ('model_id', '=', self.model_id.id),
                                  ('sh_node_option', '=', 'page')]
                        if page.get('name'):
                            domain += [('sh_attribute_name',
                                      '=', page.get('name'))]
                        if not store_model_nodes_obj.search(domain, limit=1):
                            store_model_nodes_obj.create({
                                'model_id': self.model_id.id,
                                'sh_attribute_name': page.get('name'),
                                'sh_attribute_string': page.get('string'),
                                'sh_node_option': 'page',
                            })
            if self.model_name == 'res.config.settings':
                for setting_page in doc.xpath("//div[@class='app_settings_block']"):
                    if setting_page.get('string'):
                        domain = [('sh_attribute_string', '=', setting_page.get('string')),
                                  ('model_id', '=', self.model_id.id),
                                  ('sh_node_option', '=', 'page')]
                        if setting_page.get('data-key'):
                            domain += [('sh_attribute_name', '=',
                                      setting_page.get('data-key'))]
                        if not store_model_nodes_obj.search(domain, limit=1):
                            store_model_nodes_obj.create({
                                'model_id': self.model_id.id,
                                'sh_attribute_name': setting_page.get('data-key') or '',
                                'sh_attribute_string': setting_page.get('string'),
                                'sh_node_option': 'page',
                            })

    @api.onchange('model_id')
    def _get_button(self):
        """
            A method to get button.
        """
        store_model_nodes_obj = self.env['sh.store.model.data'].sudo() # Add sudo()
        view_obj = self.env['ir.ui.view'].sudo() # Add sudo()
        if self.model_id and self.model_name:
            view_list = ['form', 'list', 'kanban']
            for view_type in view_list: # Renamed 'view' to 'view_type' to avoid confusion
                # Get the fully inherited view architecture for the model and view_type
                try:
                    res = self.env[self.model_name].sudo().get_view(
                        view_id=False, view_type=view_type) # Pass False for view_id to get default inherited view
                    doc = etree.XML(res['arch'])
                    self._get_button_and_page_data(
                        doc, view_type, store_model_nodes_obj)
                    if view_type == 'kanban':
                        self._extract_kanban_links_and_buttons(
                            res, store_model_nodes_obj)
                    self._extract_smart_buttons_and_tabs(
                        doc, store_model_nodes_obj)
                except Exception as e:
                    pass

    def write(self, vals):
        """
            A method to write values.
        """
        if self.env.context.get('disable_child_tracking_forward'):
            return super().write(vals)
        tracked_fields = [
            f for f in vals
            if f in self._fields and getattr(self._fields[f], 'tracking', False)
        ]
        initial_values = {
            rec.id: {f: rec[f] for f in tracked_fields}
            for rec in self
        }
        res = super().write(vals)
        tracking_data = self._message_track(tracked_fields, initial_values)
        for rec in self:
            if rec.access_manager_id and rec.id in tracking_data:
                _, tracking_value_ids = tracking_data[rec.id]
                if tracking_value_ids:
                    field = self.env['ir.model.fields'].search([
                        ('model', '=', rec.access_manager_id._name),
                        ('relation', '=', rec._name),
                        ('ttype', '=', 'one2many')
                    ], limit=1)
                    parent_field_label = field.field_description or rec._name
                    display_label = html_escape(str(rec.id) or rec.name or rec.display_name) \
                        if rec.display_name else str(rec.id)
                    msg = Markup(
                        "<b>Update from One2many field: %s — Id: %s</b>") % \
                        (parent_field_label, display_label)
                    rec.access_manager_id.with_context(
                        disable_child_tracking_forward=True).message_post(
                        body=msg,
                        tracking_value_ids=tracking_value_ids,
                        subtype_xmlid='mail.mt_note'
                    )
        self.env['sh.access.manager']._sh_invalidate_caches()
        return res

    def unlink(self):
        """
        A method to unlink records.
        """
        res = super().unlink()
        self.env['sh.access.manager']._sh_invalidate_caches()
        return res


class ShStoreModelData(models.Model):
    """
        A class to store model data.
    """
    _name = 'sh.store.model.data'
    _description = 'Store Model Nodes'
    _rec_name = 'sh_attribute_string'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    model_id = fields.Many2one(
        'ir.model', string='Model', index=True, ondelete='cascade',
        required=True, tracking=True,
        domain="[('model', '!=', 'sh.access.manager')]")
    sh_node_option = fields.Selection(
        [('button', 'Button'), ('page', 'Page'), ('link', 'Link'),
         ('filter', 'Filter'), ('groupby', 'Group By'),
         ('kanban_link', 'Kanban Link')],
        string="Node Option", required=True, tracking=True)
    sh_attribute_name = fields.Char('Attribute Name', tracking=True)
    sh_attribute_string = fields.Char(
        'Attribute String', required=True, tracking=True)
    sh_button_type = fields.Selection(
        [('object', 'Object'), ('action', 'Action')],
        string="Button Type", tracking=True)
    sh_is_smart_button = fields.Boolean('Smart Button', tracking=True)