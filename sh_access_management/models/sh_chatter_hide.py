# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from markupsafe import Markup

from odoo import api, fields, models
from odoo.fields import Date
from odoo.tools import html_escape


class SmartButtonList(models.Model):
    """
        A class to manage the access of smart buttons.
    """
    _name = "sh.hide.chatter"
    _description = "Smart Button List"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Navbar Name", tracking=True)
    model_ids = fields.Many2many(
        'ir.model', string="Model", tracking=True,
        domain="[('model', '!=', 'sh.access.manager')]")
    access_manager_id = fields.Many2one(
        "sh.access.manager", string="Access Manager", tracking=True)

    hide_full_chatter = fields.Boolean("Full Chatter", tracking=True)
    hide_send_msg = fields.Boolean("Send Message", tracking=True)
    hide_log_notes = fields.Boolean("Log Notes", tracking=True)
    hide_activity = fields.Boolean("Activity", tracking=True)
    hide_followers = fields.Boolean(tracking=True)
    hide_attachments = fields.Boolean("Attachments", tracking=True)

    @api.model
    def sh_checkhide_chatter(self, kwargs):
        """
        A method to check hide chatter.
        """
        user_id = kwargs.get('user_id')
        if not user_id:
            return {
                "model_restrictions": {}
            }
        user = self.env['res.users'].browse(user_id)
        company_id = kwargs.get('company_id') or self.env.company.id

        # Bypass all restrictions for system administrators
        if user.has_group('base.group_system') or user.has_group('sh_access_management.sh_access_management_manager'):
            return {
                "model_restrictions": {
                    "global": {
                        "sh_global_hide_full_chatter": False,
                        "sh_global_hide_send_message": False,
                        "sh_global_hide_log_note": False,
                        "sh_global_hide_activity": False,
                        "sh_global_hide_search_message_icon": False,
                        "sh_global_hide_attachment_icon": False,
                        "sh_global_hide_followers_icon": False,
                    }
                }
            }

        # Add domain for global restrictions
        global_user_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('responsible_user_ids', 'in', [int(user_id)]),
            ('sh_restriction_type', '=', 'user'),
            ('company_id', '=', company_id)
        ]
        global_group_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('responsible_group_ids', 'in', user.group_ids.ids),
            ('sh_restriction_type', '=', 'group'),
            ('company_id', '=', company_id)
        ]

        all_global_rules = self.env['sh.access.manager'].sudo().search(global_user_domain) | self.env['sh.access.manager'].sudo().search(global_group_domain)
        # Apply time-based filter
        all_global_rules = self.env['sh.access.manager'].sudo()._sh_filter_by_time(all_global_rules)

        # Apply global restrictions for each component
        global_restriction = any(rule.sh_global_hide_full_chatter for rule in all_global_rules)
        global_send_message_domain = any(rule.sh_global_hide_send_message for rule in all_global_rules)
        global_log_note_domain = any(rule.sh_global_hide_log_note for rule in all_global_rules)
        global_activity_domain = any(rule.sh_global_hide_activity for rule in all_global_rules)
        global_search_message_icon_domain = any(rule.sh_global_hide_search_message_icon for rule in all_global_rules)
        global_attachment_icon_domain = any(rule.sh_global_hide_attachment_icon for rule in all_global_rules)
        global_followers_icon_domain = any(rule.sh_global_hide_followers_icon for rule in all_global_rules)

        model_restrictions = {}

        # Ensure "global" key is initialized before setting global restrictions
        if "global" not in model_restrictions:
            model_restrictions["global"] = {}

        # Apply model-wise restrictions
        user_domain = [
            ('access_manager_id.active_rule', '=', True),
            '|', ('access_manager_id.sh_expiry_date', '=', False), ('access_manager_id.sh_expiry_date', '>=', Date.today()),
            ('access_manager_id.responsible_user_ids', 'in', [int(user_id)]),
            ('access_manager_id.sh_restriction_type', '=', 'user'),
            ('access_manager_id.company_id', '=', company_id)
        ]
        group_domain = [
            ('access_manager_id.active_rule', '=', True),
            '|', ('access_manager_id.sh_expiry_date', '=', False), ('access_manager_id.sh_expiry_date', '>=', Date.today()),
            ('access_manager_id.responsible_group_ids', 'in', user.group_ids.ids),
            ('access_manager_id.sh_restriction_type', '=', 'group'),
            ('access_manager_id.company_id', '=', company_id)
        ]
        find_records = self.env['sh.hide.chatter'].sudo().search(user_domain) | self.env['sh.hide.chatter'].sudo().search(group_domain)
        # Apply time-based filter on the parent Access Manager records
        find_records = find_records.filtered(lambda r: r.access_manager_id._sh_is_within_time_window())

        for record in find_records:
            for model in record.sudo().model_ids:
                model_name = model.model
                # Add Model Wise Restrictions
                if model_name not in model_restrictions:
                    model_restrictions[model_name] = {
                        "hide_full_chatter": record.hide_full_chatter,
                        "hide_send_msg": record.hide_send_msg,
                        "hide_log_notes": record.hide_log_notes,
                        "hide_activity": record.hide_activity,
                        "hide_followers": record.hide_followers,
                        "hide_attachments": record.hide_attachments,
                    }
                else:
                    model_restrictions[model_name]["hide_full_chatter"] |= record.hide_full_chatter
                    model_restrictions[model_name]["hide_send_msg"] |= record.hide_send_msg
                    model_restrictions[model_name]["hide_log_notes"] |= record.hide_log_notes
                    model_restrictions[model_name]["hide_activity"] |= record.hide_activity
                    model_restrictions[model_name]["hide_followers"] |= record.hide_followers
                    model_restrictions[model_name]["hide_attachments"] |= record.hide_attachments

        # Apply global restrictions if found
        if global_restriction:
            model_restrictions["global"]["sh_global_hide_full_chatter"] = True
        if global_send_message_domain:
            model_restrictions["global"]["sh_global_hide_send_message"] = True
        if global_log_note_domain:
            model_restrictions["global"]["sh_global_hide_log_note"] = True
        if global_activity_domain:
            model_restrictions["global"]["sh_global_hide_activity"] = True
        if global_search_message_icon_domain:
            model_restrictions["global"]["sh_global_hide_search_message_icon"] = True
        if global_attachment_icon_domain:
            model_restrictions["global"]["sh_global_hide_attachment_icon"] = True
        if global_followers_icon_domain:
            model_restrictions["global"]["sh_global_hide_followers_icon"] = True
        
        return {
            "model_restrictions": model_restrictions
        }

    def write(self, vals):
        """
        A method to write values.
        """
        if self.env.context.get('disable_child_tracking_forward'):
            res = super().write(vals)
            self.env['sh.access.manager']._sh_invalidate_caches()
            return res
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
