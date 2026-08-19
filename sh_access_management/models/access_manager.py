# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from markupsafe import Markup
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from odoo import _, api, exceptions, fields, models, tools
from odoo.exceptions import AccessError
from odoo.fields import Date
from odoo.tools import html_escape
import logging

_logger = logging.getLogger(__name__)

# Timezone list matching Odoo core (Etc/* entries at end)
_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


class AccessManager(models.Model):
    """
        A class to manage the access of users.
    """
    _name = "sh.access.manager"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Access Management"

    name = fields.Char("Name", tracking=True)

    sh_restriction_type = fields.Selection([
        ('user', 'User'),
        ('group', 'Group'),
    ], default='user', string='Restriction Type', tracking=True)

    responsible_user_ids = fields.Many2many(
        'res.users',
        'sh_access_manager_responsible_user_rel',
        'sh_access_manager_id',
        'responsible_user_id',
        string="Users",
        tracking=True)

    responsible_group_ids = fields.Many2many(
        'res.groups',
        'sh_access_manager_responsible_group_rel',
        'sh_access_manager_id',
        'responsible_group_id',
        string="Groups",
        tracking=True)

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )

    created_by = fields.Many2one(
        "res.users", string="Created By", tracking=True)
    active_rule = fields.Boolean("Active", default=True, tracking=True)
    sh_expiry_date = fields.Date("Expiry Date", tracking=True)
    sh_readonly = fields.Boolean("Readonly", tracking=True)
    sh_disable_developer_mode = fields.Boolean(
        "Disable Developer Mode", tracking=True)

    sh_global_hide_full_chatter = fields.Boolean(
        "Full Chatter", tracking=True)
    sh_disable_user_login = fields.Boolean("Disable Login", tracking=True)
    sh_restrict_xmlrpc = fields.Boolean("Restrict XML-RPC / Script Access", tracking=True)

    # Time based restriction
    sh_restrict_by_time = fields.Boolean("Restrict based on time?", tracking=True)
    sh_time_from = fields.Float("Time From (HH:MM)", tracking=True)
    sh_time_to = fields.Float("Time To (HH:MM)", tracking=True)
    sh_timezone = fields.Selection(
        _tzs,
        string="Timezone",
        default=lambda self: self.env.user.tz or 'UTC',
        tracking=True
    )

    def _sh_is_within_time_window(self):
        """
        Returns True if the rule's restriction should be ACTIVATED right now.
        - If sh_restrict_by_time = False → always returns True (rule is always on)
        - If sh_restrict_by_time = True  → ONLY returns True if current time is in the window.
        """
        self.ensure_one()
        if not self.sh_restrict_by_time:
            return True  # Rule is always active

        tz_name = self.sh_timezone or 'UTC'
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.UTC

        now_local = datetime.now(tz)
        current_minutes = now_local.hour * 60 + now_local.minute

        def to_minutes(float_val):
            h = int(float_val)
            m = round((float_val - h) * 60)
            return h * 60 + m

        from_min = to_minutes(self.sh_time_from or 0.0)
        to_min = to_minutes(self.sh_time_to or 0.0)
        

        # Check if expiration date is today and if we are past the 'to' time
        if self.sh_expiry_date == Date.today():
            if current_minutes > to_min:
                return False

        # Check if the restriction should BE ACTIVE based on time
        if from_min <= to_min:
            # Normal day window: e.g. 09:00 to 18:00
            # If current time is 10:00 -> returns True (activate rule)
            # If current time is 20:00 -> returns False (do not activate rule)
            return from_min <= current_minutes <= to_min
        else:
            # Overnight window: e.g. 22:00 to 06:00
            # If current time is 23:00 or 05:00 -> returns True (activate rule)
            return current_minutes >= from_min or current_minutes <= to_min

    @api.model
    def _sh_filter_by_time(self, rules):
        """
        Filter a recordset of sh.access.manager records,
        keeping only those whose time window is currently active.
        Rules with sh_restrict_by_time=False are always kept.
        """
        return rules.filtered(lambda r: r._sh_is_within_time_window())

    @api.onchange('sh_expiry_date')
    def onchange_sh_expiry_date(self):
        if self.sh_expiry_date:
            if self.sh_expiry_date < Date.today():
                self.active_rule = False
            elif self.sh_expiry_date >= Date.today():
                self.active_rule = True

    # Global Access
    sh_global_hide_add_property = fields.Boolean(
        "Hide Add Property", tracking=True)
    sh_global_hide_import = fields.Boolean("Hide Import", tracking=True)
    sh_global_hide_export = fields.Boolean(
        "Hide Export", tracking=True)
    sh_global_hide_print_button = fields.Boolean(
        "Hide Print Button", tracking=True)
    sh_global_hide_action_button = fields.Boolean(
        "Hide Action Button", tracking=True)
    sh_global_hide_send_message = fields.Boolean(
        "Hide Send Message", tracking=True)
    sh_global_hide_log_note = fields.Boolean("Hide Log note", tracking=True)
    sh_global_hide_activity = fields.Boolean("Hide Activity", tracking=True)
    sh_global_hide_search_message_icon = fields.Boolean("Hide Search Message Icon", tracking=True)
    sh_global_hide_attachment_icon = fields.Boolean("Hide Attachment Icon", tracking=True)
    sh_global_hide_followers_icon = fields.Boolean("Hide Followers Icon", tracking=True)
    sh_global_hide_filter = fields.Boolean("Hide Filter", tracking=True)
    sh_global_hide_group = fields.Boolean("Hide Group By", tracking=True)
    sh_global_hide_search_panel = fields.Boolean(
        "Hide Search Panel", tracking=True)
    sh_global_hide_custom_filter_option = fields.Boolean(
        "Hide Custom Filter Option", tracking=True)
    sh_global_hide_custom_group_by_option = fields.Boolean(
        "Hide Custom Group By Option", tracking=True)
    sh_global_hide_spreadsheet = fields.Boolean(
        "Hide Spreadsheet", tracking=True)
    sh_global_hide_field_credit_edit = fields.Boolean(
        "Hide Create / Edit", tracking=True)
    sh_global_hide_favorite_edit = fields.Boolean(
        "Hide Favorite Edit", tracking=True)
    sh_global_hide_favourite = fields.Boolean(
        "Hide Favorite Menu", tracking=True)

    sh_global_hide_create = fields.Boolean("Hide Create", tracking=True)
    sh_global_hide_delete = fields.Boolean("Hide Delete", tracking=True)
    sh_global_hide_duplicate = fields.Boolean("Hide Duplicate", tracking=True)
    sh_global_hide_archive = fields.Boolean("Hide Archive", tracking=True)
    sh_global_hide_unarchive = fields.Boolean("Hide Unarchive", tracking=True)

    sh_is_spreadsheet_installed = fields.Boolean(
        compute="_compute_is_spreadsheet_installed",
        store=False
    )

    @api.depends_context("uid")
    def _compute_is_spreadsheet_installed(self):
        installed = self.env['ir.module.module'].sudo().search_count([
            ("name", "=", "spreadsheet_edition"),
            ("state", "=", "installed"),
        ]) > 0
        for rec in self:
            rec.sh_is_spreadsheet_installed = installed

    # Pages
    sh_hide_menu_ids = fields.Many2many(
        comodel_name="ir.ui.menu",
        string="Hide Menu",
        tracking=True)

    sh_access_model_line = fields.One2many(
        "sh.access.model", 'access_manager_id', string="Access Model",
        tracking=True)

    sh_field_access_line = fields.One2many(
        "sh.field.access", 'access_manager_id', string="Field Access",
        tracking=True)

    sh_navbar_button_line = fields.One2many(
        'sh.navbar.buttons.access', 'access_manager_id', 'Navbar Button Access',
        tracking=True)

    sh_hide_chatter_line = fields.One2many(
        "sh.hide.chatter", 'access_manager_id', string="Hide Chatters",
        tracking=True)
    sh_hide_filter_line = fields.One2many(
        "sh.filter.access", 'access_manager_id', string="Filter Access",
        tracking=True)

    sh_conditional_access_ids = fields.One2many(
        "sh.conditional.domain", 'sh_access_manager_id', string="Conditional Access Rules",
        tracking=True)

    @api.model
    def sh_check_rule_expiry(self):
        """
            A method to check rule expiry.
        """
        expired_rules = self.search([
            ('sh_expiry_date', '<=', Date.today()),
            ('active_rule', '=', True)
        ])
        if expired_rules:
            expired_rules.write({'active_rule': False})

    @api.model_create_multi
    def create(self, vals_list):
        """
        Prevent adding admin users in `responsible_user_ids` during record creation.
        """
        admin_users = self.env.ref('base.group_system').user_ids
        admin_group = self.env.ref('base.group_system') 

        for vals in vals_list:
            if 'responsible_user_ids' in vals:
                new_user_ids = set()

                for operation in vals['responsible_user_ids']:
                    if operation[0] == 6:  # Replace all
                        new_user_ids.update(operation[2])
                    elif operation[0] == 4:  # Add single
                        new_user_ids.add(operation[1])

                restricted_admins = admin_users.filtered(
                    lambda u: u.id in new_user_ids)
                if restricted_admins:
                    raise exceptions.UserError(
                        _("You cannot add an administrator to the a list.")
                    )

            if 'responsible_group_ids' in vals:
                new_group_ids = set()
                for operation in vals['responsible_group_ids']:
                    if operation[0] == 6:  # Replace all
                        new_group_ids.update(operation[2])
                    elif operation[0] == 4:  # Add single
                        new_group_ids.add(operation[1])

                if admin_group.id in new_group_ids:
                    raise exceptions.UserError(
                        _("You cannot add an Administrator group to the list.")
                    )

        res = super().create(vals_list)
        self._sh_invalidate_caches()
        return res

    def _mail_track(self, tracked_fields, initial_values):
        """
            A method to track mail.
        """
        # Step 1: Remove One2many fields before calling super
        filtered_fields = {
            k: v for k, v in tracked_fields.items()
            if v.get('type') != 'one2many'
        }
        filtered_initial_values = {
            k: v for k, v in initial_values.items()
            if k in filtered_fields
        }

        return super()._mail_track(filtered_fields, filtered_initial_values)

    def write(self, vals):
        """
            A method to write values.
        """
        # Prevent assigning admin users
        if 'responsible_user_ids' in vals:
            admin_users = self.env.ref('base.group_system').user_ids
            for record in self:
                new_user_ids = set()
                for operation in vals['responsible_user_ids']:
                    if operation[0] == 6:
                        new_user_ids.update(operation[2])
                    elif operation[0] == 4:
                        new_user_ids.add(operation[1])
                restricted_admins = admin_users.filtered(
                    lambda u: u.id in new_user_ids)
                if restricted_admins:
                    raise exceptions.UserError(
                        _("You cannot add an Administrator to the a list."))

        if 'responsible_group_ids' in vals:
            admin_group = self.env.ref('base.group_system')
            new_group_ids = set()
            for operation in vals['responsible_group_ids']:
                if operation[0] == 6:
                    new_group_ids.update(operation[2])
                elif operation[0] == 4:
                    new_group_ids.add(operation[1])

            if admin_group.id in new_group_ids:
                raise exceptions.UserError(
                    _("You cannot add an Administrator group to the list.")
                )

        # Collect inline-created O2M record placeholders before write
        created_map = {}  # {record.id: {field_name: count}}

        for rec in self:
            for field_name, field in self._fields.items():
                if field.type == 'one2many' and field_name in vals:
                    commands = vals[field_name]
                    count = sum(1 for cmd in commands if cmd[0]
                              == 0 and isinstance(cmd[2], dict))
                    if count:
                        created_map.setdefault(rec.id, {})[field_name] = count

        res = super().write(vals)

        # Post-write: log correct records per field
        for rec in self:
            if rec.id in created_map:
                for field_name, count in created_map.get(rec.id, {}).items():
                    new_recs = rec[field_name].sorted(
                        key='id', reverse=True)[:count]
                    # to restore original order
                    new_recs = new_recs.sorted(key='id')

                    for new in new_recs:
                        model_desc = self.env[new._name]._description or new._name
                        msg_content = _("New → %(name)s,%(id)s (%(model_desc)s)") % {
                            'name': html_escape(new._name),
                            'id': new.id,
                            'model_desc': html_escape(model_desc)
                        }
                        msg = Markup(
                            "<ul><li><b>%(msg_content)s</b></li></ul>") % {
                                'msg_content': msg_content}
                        rec.message_post(body=msg, subtype_xmlid="mail.mt_note")

        self._sh_invalidate_caches()
        return res

    def unlink(self):
        """
            A method to unlink.
        """
        self.sh_navbar_button_line.unlink()
        res = super().unlink()
        self._sh_invalidate_caches()
        return res

    def _sh_invalidate_caches(self):
        """ Force cache invalidation across all workers. """
        self.env.registry.clear_cache('default', 'templates', 'groups', 'assets')
        new_version = fields.Datetime.now().isoformat()
        self.env['ir.config_parameter'].sudo().set_param('sh_access_management.cache_version', new_version)

    @api.model
    def get_access_restrictions(self, kwargs):
        """
        Dynamically prepare and return access restrictions for the user.
        Args:
            kwargs (dict): Contains user_id and optional company_id.
        Returns:
            dict: Restrictions based on user-specific and global rules.
        """
        user_id = kwargs.get("user_id")
        user = self.env['res.users'].browse(user_id)
        company_id = kwargs.get("company_id") or self.env.company.id

        if not user_id:
            raise ValueError("User ID is required.")

        # Bypass all restrictions for system administrators
        if user.has_group('base.group_system') or user.has_group('sh_access_management.sh_access_management_manager'):
            return {
                "model_restrictions": {
                    "disable_developer_mode": False,
                    "global_hide_full_chatter": False,
                    "sh_readonly": False,
                    "global_hide_custom_filter": False,
                    "global_hide_custom_group_by": False,
                    "global_hide_filter": False,
                    "global_hide_group_by": False,
                    "global_hide_spreadsheet": False,
                    "sh_global_hide_field_credit_edit": False,
                    "sh_global_hide_favorite_edit": False,
                    "sh_global_hide_create": False,
                    "sh_global_hide_delete": False,
                    "sh_global_hide_duplicate": False,
                    "sh_global_hide_archive": False,
                    "sh_global_hide_unarchive": False,
                    "sh_restrict_xmlrpc": False,
                }
            }

        user_domain = [
            ('responsible_user_ids', 'in', [user_id]),
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('sh_restriction_type', '=', 'user'),
        ]
        group_domain = [
            ('responsible_group_ids', 'in', user.group_ids.ids),
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('sh_restriction_type', '=', 'group'),
        ]

        if company_id:
            user_domain.append(('company_id', '=', company_id))
            group_domain.append(('company_id', '=', company_id))

        user_rules = self.search(user_domain)
        group_rules = self.search(group_domain)

        all_rules = user_rules | group_rules
        all_rules = self._sh_filter_by_time(all_rules)

        disable_developer_mode = any(rule.sh_disable_developer_mode for rule in all_rules)
        global_hide_full_chatter = any(rule.sh_global_hide_full_chatter for rule in all_rules)
        sh_readonly = any(rule.sh_readonly for rule in all_rules)
        global_hide_custom_filter = any(rule.sh_global_hide_custom_filter_option for rule in all_rules)
        global_hide_custom_group_by = any(rule.sh_global_hide_custom_group_by_option for rule in all_rules)
        global_hide_filter = any(rule.sh_global_hide_filter for rule in all_rules)
        global_hide_group_by = any(rule.sh_global_hide_group for rule in all_rules)
        global_hide_search_panel = any(rule.sh_global_hide_search_panel for rule in all_rules)
        global_hide_spreadsheet = any(rule.sh_global_hide_spreadsheet for rule in all_rules)
        sh_global_hide_field_credit_edit = any(rule.sh_global_hide_field_credit_edit for rule in all_rules)
        sh_global_hide_favorite_edit = any(rule.sh_global_hide_favorite_edit for rule in all_rules)
        sh_global_hide_favourite = any(rule.sh_global_hide_favourite for rule in all_rules)
        sh_global_hide_create = any(rule.sh_global_hide_create for rule in all_rules)
        sh_global_hide_delete = any(rule.sh_global_hide_delete for rule in all_rules)
        sh_global_hide_duplicate = any(rule.sh_global_hide_duplicate for rule in all_rules)
        sh_global_hide_archive = any(rule.sh_global_hide_archive for rule in all_rules)
        sh_global_hide_unarchive = any(rule.sh_global_hide_unarchive for rule in all_rules)
        sh_restrict_xmlrpc = any(rule.sh_restrict_xmlrpc for rule in all_rules)

        return {
            "model_restrictions": {
                "disable_developer_mode": disable_developer_mode,
                "global_hide_full_chatter": global_hide_full_chatter,
                "sh_readonly": sh_readonly,
                "global_hide_custom_filter": global_hide_custom_filter,
                "global_hide_custom_group_by": global_hide_custom_group_by,
                "global_hide_filter": global_hide_filter,
                "global_hide_group_by": global_hide_group_by,
                "global_hide_search_panel": global_hide_search_panel,
                "global_hide_spreadsheet": global_hide_spreadsheet,
                "sh_global_hide_field_credit_edit": sh_global_hide_field_credit_edit,
                "sh_global_hide_favorite_edit": sh_global_hide_favorite_edit,
                "sh_global_hide_favourite": sh_global_hide_favourite,
                "sh_global_hide_create": sh_global_hide_create,
                "sh_global_hide_delete": sh_global_hide_delete,
                "sh_global_hide_duplicate": sh_global_hide_duplicate,
                "sh_global_hide_archive": sh_global_hide_archive,
                "sh_global_hide_unarchive": sh_global_hide_unarchive,
                "sh_restrict_xmlrpc": sh_restrict_xmlrpc,
            }
        }

    @api.model
    def get_hidden_views(self, model=None, user_id=None):
        if not model or not user_id:
            return []
            
        user = self.env['res.users'].browse(user_id)
        if self.env.su or user.has_group('base.group_system') or user.has_group('sh_access_management.sh_access_management_manager'):
            return []
        
        user_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('responsible_user_ids', 'in', [int(user_id)]),
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

        access_managers = self.sudo().search(user_domain) | self.sudo().search(group_domain)
        access_managers = self._sh_filter_by_time(access_managers)
        hidden_views = []
        
        if access_managers:
            for manager in access_managers:
                for line in manager.sh_access_model_line:
                    if line.model_id.model == model:
                        for view in line.view_ids:
                            if view.technical_name not in hidden_views:
                                hidden_views.append(view.technical_name)
                                
        return hidden_views

    @api.model
    # ormcache is disabled here because rules vary by the minute/hour if sh_restrict_by_time is enabled.
    # @tools.ormcache('self.env.uid', 'self.env.company.id', 'model_name')
    def get_model_field_rules(self, model_name):
        user = self.env.user

        # Allow bypass for testing even if user is admin
        if (user.has_group('base.group_system') or user.has_group('sh_access_management.sh_access_management_manager')):
            return {}

        common_domain = [
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('company_id', '=', self.env.company.id),
        ]
        
        user_spec_domain = common_domain + [
            ('responsible_user_ids', 'in', user.ids),
            ('sh_restriction_type', '=', 'user')
        ]
        group_spec_domain = common_domain + [
            ('responsible_group_ids', 'in', user.group_ids.ids),
            ('sh_restriction_type', '=', 'group')
        ]

        access_managers = self.sudo().search(user_spec_domain) | self.sudo().search(group_spec_domain)
        access_managers = self._sh_filter_by_time(access_managers)
        
        if not access_managers:
            return {}

        field_rules = self.env['sh.field.access'].sudo().search([
            ('access_manager_id', 'in', access_managers.ids),
            ('model_id.model', '=', model_name)
        ])
        
        res = {}
        for rule in field_rules:
            for field in rule.field_ids:
                res[field.name] = {
                    'invisible': rule.invisible,
                    'readonly': rule.readonly,
                    'required': rule.required,
                    'no_open': rule.sh_hide_external_links,
                    'no_create_edit': rule.sh_hide_create_edit,
                }
        return res

    # ============================================================
    # DASHBOARD METHODS
    # ============================================================

    @api.model
    def get_dashboard_data(self, company_id=None):
        """
        Main aggregator called once per dashboard load.

        :param int company_id: optional; defaults to env.company
        :returns: dict with all panels' data
        """
        company = self.env['res.company'].browse(company_id) if company_id else self.env.company
        return {
            'company': {'id': company.id, 'name': company.name},
            'kpis': self._sh_get_kpis(company),
            'charts': {
                'restriction_type': self._sh_get_restriction_type_split(company),
                'creation_trend': self._sh_get_creation_trend(company, months=6),
            },
            'top_models': self._sh_get_top_restricted_models(company, limit=20),
            'heatmap': self._sh_get_heatmap(company, limit=20),
            'insights': self._sh_get_access_insights(company),
            'recent_activity': self._sh_get_recent_activity(company, limit=10),
            'top_users': self._sh_get_top_restricted_users(company, limit=10),
            'fetched_at': fields.Datetime.now().isoformat() + 'Z',
        }

    def _sh_get_kpis(self, company):
        today = Date.today()
        week = today + relativedelta(days=7)
        Rule = self.sudo()
        base = [('company_id', '=', company.id)]

        return {
            'total':         Rule.search_count(base),
            'active':        Rule.search_count(base + [('active_rule', '=', True)]),
            'inactive':      Rule.search_count(base + [('active_rule', '=', False)]),
            'expiring_7d':   Rule.search_count(base + [
                                ('sh_expiry_date', '>=', today),
                                ('sh_expiry_date', '<=', week),
                                ('active_rule', '=', True),
                                                 ]),
            'expired_today': Rule.search_count(base + [('sh_expiry_date', '=', today)]),
            'by_user':       Rule.search_count(base + [('sh_restriction_type', '=', 'user')]),
            'by_group':      Rule.search_count(base + [('sh_restriction_type', '=', 'group')]),
            'time_based':    Rule.search_count(base + [('sh_restrict_by_time', '=', True)]),
            'login_disabled': Rule.search_count(base + [('sh_disable_user_login', '=', True)]),
            'total_trend_pct': self._sh_compute_trend(Rule, base),
        }

    def _sh_compute_trend(self, Rule, base_domain):
        """Compare last 30 days vs prior 30 days. Returns signed percentage."""
        today = Date.today()
        d30 = today - relativedelta(days=30)
        d60 = today - relativedelta(days=60)
        current = Rule.search_count(base_domain + [('create_date', '>=', d30)])
        prior = Rule.search_count(base_domain + [('create_date', '>=', d60), ('create_date', '<', d30)])
        if prior == 0:
            return 100 if current else 0
        return round(((current - prior) / prior) * 100, 1)

    def _sh_get_restriction_type_split(self, company):
        Rule = self.sudo()
        groups = Rule._read_group(
            domain=[('company_id', '=', company.id)],
            groupby=['sh_restriction_type'],
            aggregates=['__count'],
        )
        selection = dict(self._fields['sh_restriction_type'].selection)
        return [
            {'label': selection.get(rtype or '', rtype or 'Unknown'), 'value': cnt}
            for rtype, cnt in groups
        ]

    def _sh_get_creation_trend(self, company, months=6):
        today = Date.today()
        start = today.replace(day=1) - relativedelta(months=months - 1)
        groups = self.sudo()._read_group(
            domain=[('company_id', '=', company.id), ('create_date', '>=', start)],
            groupby=['create_date:month'],
            aggregates=['__count'],
        )
        # _read_group returns (date_trunc_val, count) — date_trunc_val is a date object
        counts = {}
        for date_val, cnt in groups:
            if date_val:
                key = date_val.strftime('%b %Y') if hasattr(date_val, 'strftime') else str(date_val)
                counts[key] = cnt
        result = []
        cursor = start
        for _i in range(months):
            key = cursor.strftime('%b %Y')
            result.append({'label': cursor.strftime('%b'), 'value': counts.get(key, 0)})
            cursor += relativedelta(months=1)
        return result

    def _sh_get_top_restricted_models(self, company, limit=20):
        """Aggregate distinct rule counts per model across access_model + field_access tables."""
        self.env.cr.execute("""
            WITH rule_models AS (
                SELECT m.model AS model, m.name AS name, am.access_manager_id AS rule_id
                FROM sh_access_model am
                JOIN ir_model m ON m.id = am.model_id
                JOIN sh_access_manager amgr ON amgr.id = am.access_manager_id
                WHERE amgr.company_id = %s AND amgr.active_rule = TRUE
                UNION
                SELECT m.model AS model, m.name AS name, fa.access_manager_id AS rule_id
                FROM sh_field_access fa
                JOIN ir_model m ON m.id = fa.model_id
                JOIN sh_access_manager amgr ON amgr.id = fa.access_manager_id
                WHERE amgr.company_id = %s AND amgr.active_rule = TRUE
            )
            SELECT model, MAX(name::text) AS name, COUNT(DISTINCT rule_id) AS cnt
            FROM rule_models
            GROUP BY model
            ORDER BY cnt DESC, model ASC
            LIMIT %s
        """, (company.id, company.id, limit))
        return [{'model': r[0], 'name': r[1] or r[0], 'count': r[2]}
                for r in self.env.cr.fetchall()]

    def _sh_get_heatmap(self, company, limit=20):
        """
        Returns: [{'model': 'sale.order', 'name': '...', 'vals': [r, w, c, d, ro, fh, vh], 'total': N}, ...]
        Columns: Read, Write, Create, Delete, Readonly, FieldHide, ViewHide
        """
        base_domain = [('company_id', '=', company.id), ('active_rule', '=', True)]
        all_rules = self.sudo().search(base_domain)

        # Collect per-model stats using ORM — avoids raw SQL table name guessing
        model_stats = defaultdict(lambda: {
            'name': '', 'rules': set(),
            'create': 0, 'delete': 0, 'readonly': 0,
            'field_hide': 0, 'field_ro': 0, 'view_hide': 0,
        })

        for rule in all_rules:
            flags = {
                'create': rule.sh_global_hide_create,
                'delete': rule.sh_global_hide_delete,
                'readonly': rule.sh_readonly,
            }
            # Model access lines
            for line in rule.sh_access_model_line:
                mname = line.model_id.model
                if not mname:
                    continue
                s = model_stats[mname]
                s['name'] = s['name'] or line.model_id.name or mname
                s['rules'].add(rule.id)
                if flags['create']:
                    s['create'] += 1
                if flags['delete']:
                    s['delete'] += 1
                if flags['readonly']:
                    s['readonly'] += 1
                s['view_hide'] += len(line.view_ids)

            # Field access lines
            for fa in rule.sh_field_access_line:
                mname = fa.model_id.model
                if not mname:
                    continue
                s = model_stats[mname]
                s['name'] = s['name'] or fa.model_id.name or mname
                s['rules'].add(rule.id)
                if fa.invisible:
                    s['field_hide'] += len(fa.field_ids)
                if fa.readonly:
                    s['field_ro'] += len(fa.field_ids)

        result = []
        for model, s in model_stats.items():
            read_cnt = s['view_hide']
            write_cnt = s['readonly'] + s['field_ro']
            total = len(s['rules'])
            result.append({
                'model': model,
                'name': s['name'] or model,
                'vals': [read_cnt, write_cnt, s['create'], s['delete'], s['readonly'], s['field_hide'], s['view_hide']],
                'total': total,
            })
        result.sort(key=lambda x: -x['total'])
        return result[:limit]

    def _sh_get_access_insights(self, company):
        """Audit summary items + computed Config Score (0-100)."""
        Rule = self.sudo()
        today = Date.today()
        domain = [('company_id', '=', company.id)]

        expired_not_archived = Rule.search_count(domain + [
            ('sh_expiry_date', '<', today),
            ('active_rule', '=', True),
        ])
        expiring_7d = Rule.search_count(domain + [
            ('sh_expiry_date', '>=', today),
            ('sh_expiry_date', '<=', today + relativedelta(days=7)),
        ])
        time_based_rules = Rule.search(domain + [('sh_restrict_by_time', '=', True)])
        time_now_active = sum(1 for r in time_based_rules if r._sh_is_within_time_window())

        admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
        rules_targeting_admin = 0
        if admin_group:
            admin_user_ids = admin_group.sudo().user_ids.ids
            if admin_user_ids:
                rules_targeting_admin = Rule.search_count(
                    domain + [('responsible_user_ids', 'in', admin_user_ids)]
                )

        total_companies = self.env['res.company'].sudo().search_count([])
        active_rules = Rule.search([('active_rule', '=', True)])
        rules_per_company = len(set(active_rules.mapped('company_id').ids))

        model_lines = self.env['sh.access.model'].sudo().search([
            ('access_manager_id.company_id', '=', company.id),
            ('access_manager_id.active_rule', '=', True),
        ])
        models_covered = len(set(model_lines.mapped('model_id').ids))

        field_count = self.env['sh.field.access'].sudo().search_count([
            ('access_manager_id.company_id', '=', company.id),
            ('access_manager_id.active_rule', '=', True),
        ])

        user_ids = set()
        for r in Rule.search(domain):
            user_ids |= set(r.responsible_user_ids.ids)
            for g in r.responsible_group_ids:
                user_ids |= set(g.sudo().user_ids.ids)
        users_affected = len(user_ids)

        xmlrpc_rules = Rule.search_count(domain + [('sh_restrict_xmlrpc', '=', True)])

        cache_param = self.env['ir.config_parameter'].sudo().get_param(
            'sh_access_management.cache_version'
        )
        cache_minutes_ago = 0
        if cache_param:
            try:
                cache_minutes_ago = int(
                    (fields.Datetime.now() - fields.Datetime.from_string(cache_param)).total_seconds() / 60
                )
            except Exception:
                cache_minutes_ago = 0

        recently_updated = Rule.search_count(domain + [
            ('write_date', '>=', today - relativedelta(days=7)),
        ])

        items = [
            {
                'icon': 'fa-shield',
                'status': 'good' if not rules_targeting_admin else 'warn',
                'title': _('Admin Protection'),
                'value': _('All admins excluded') if not rules_targeting_admin
                         else _('%d rules target admin') % rules_targeting_admin,
                'detail': _('Administrators should never be restricted'),
            },
            {
                'icon': 'fa-building',
                'status': 'good' if rules_per_company >= total_companies else 'info',
                'title': _('Multi-Company Coverage'),
                'value': '%d / %d %s' % (rules_per_company, total_companies, _('companies')),
                'detail': _('Companies with at least one active rule'),
            },
            {
                'icon': 'fa-refresh',
                'status': 'good' if cache_minutes_ago < 60 else 'info',
                'title': _('Cache Status'),
                'value': _('Fresh') if cache_minutes_ago < 60 else _('%d min old') % cache_minutes_ago,
                'detail': _('Cache invalidated %d min ago') % cache_minutes_ago,
            },
            {
                'icon': 'fa-cubes',
                'status': 'info',
                'title': _('Models Covered'),
                'value': _('%d models') % models_covered,
                'detail': _('Distinct models touched by rules'),
            },
            {
                'icon': 'fa-users',
                'status': 'info',
                'title': _('Users Affected'),
                'value': _('%d users') % users_affected,
                'detail': _('Across user-rules and group-rules'),
            },
            {
                'icon': 'fa-lock',
                'status': 'info',
                'title': _('Field Restrictions'),
                'value': _('%d fields') % field_count,
                'detail': _('Across configured models'),
            },
            {
                'icon': 'fa-clock-o',
                'status': 'info',
                'title': _('Time-Based Active Now'),
                'value': _('%d rules') % time_now_active,
                'detail': _('Currently within their time window'),
            },
            {
                'icon': 'fa-calendar',
                'status': 'warn' if expiring_7d else 'good',
                'title': _('Expiring This Week'),
                'value': _('%d rules') % expiring_7d,
                'detail': _('Review needed') if expiring_7d else _('No expirations soon'),
            },
            {
                'icon': 'fa-eraser',
                'status': 'warn' if expired_not_archived else 'good',
                'title': _('Expired Not Archived'),
                'value': _('%d rules') % expired_not_archived,
                'detail': _('Run "Cleanup Expired" action') if expired_not_archived
                          else _('All expired rules deactivated'),
            },
            {
                'icon': 'fa-history',
                'status': 'good',
                'title': _('Recently Updated'),
                'value': _('%d rules this week') % recently_updated,
                'detail': _('Rules updated in the last 7 days'),
            },
            {
                'icon': 'fa-file-text-o',
                'status': 'good',
                'title': _('Audit Trail'),
                'value': _('Enabled'),
                'detail': _('All field changes tracked via chatter'),
            },
            {
                'icon': 'fa-shield',
                'status': 'good' if xmlrpc_rules else 'info',
                'title': _('XML-RPC Restrictions'),
                'value': _('%d rules active') % xmlrpc_rules,
                'detail': _('API/script access controlled'),
            },
        ]

        # Config Score (weighted, max 100)
        weights = [
            (15, not rules_targeting_admin),
            (10, rules_per_company >= total_companies and total_companies > 0),
            (15, expired_not_archived == 0),
            (5,  cache_minutes_ago < 60),
            (10, True),  # audit trail always on
            (10, xmlrpc_rules > 0),
            (15, models_covered > 0),
            (10, users_affected > 0),
            (10, recently_updated > 0),
        ]
        score = sum(w for w, ok in weights if ok)
        if score >= 90:
            rating, rating_color = _('Excellent'), '#017E84'
        elif score >= 75:
            rating, rating_color = _('Good'), '#017E84'
        elif score >= 50:
            rating, rating_color = _('Fair'), '#F0AD4E'
        else:
            rating, rating_color = _('Poor'), '#D9534F'

        return {
            'items': items,
            'score': score,
            'rating': rating,
            'rating_color': rating_color,
        }

    def _sh_get_recent_activity(self, company, limit=10):
        rules = self.sudo().search(
            [('company_id', '=', company.id)],
            order='write_date desc',
            limit=limit,
        )
        today = Date.today()
        result = []
        for r in rules:
            if not r.active_rule:
                status = 'inactive'
            elif r.sh_expiry_date and r.sh_expiry_date < today:
                status = 'expired'
            elif r.sh_expiry_date and (r.sh_expiry_date - today).days <= 7:
                status = 'expiring'
            elif r.sh_restrict_by_time:
                status = 'time'
            else:
                status = 'active'

            applied_to = ''
            if r.sh_restriction_type == 'user':
                applied_to = _('%d users') % len(r.responsible_user_ids)
            else:
                applied_to = ', '.join(r.responsible_group_ids.mapped('name')[:2]) or _('No group')

            result.append({
                'id': r.id,
                'name': r.name or _('Unnamed Rule'),
                'type': r.sh_restriction_type or 'user',
                'applied_to': applied_to,
                'expiry': r.sh_expiry_date.strftime('%Y-%m-%d') if r.sh_expiry_date else '—',
                'status': status,
                'write_date': fields.Datetime.to_string(r.write_date),
            })
        return result

    def _sh_get_top_restricted_users(self, company, limit=10):
        """Aggregate rule-count per user across direct + via groups."""
        self.env.cr.execute("""
            SELECT u.id, COUNT(DISTINCT rel.sh_access_manager_id) AS cnt
            FROM sh_access_manager_responsible_user_rel rel
            JOIN sh_access_manager amgr ON amgr.id = rel.sh_access_manager_id
            JOIN res_users u ON u.id = rel.responsible_user_id
            WHERE amgr.company_id = %s AND amgr.active_rule = TRUE
            GROUP BY u.id
            ORDER BY cnt DESC
            LIMIT %s
        """, (company.id, limit))
        rows = self.env.cr.fetchall()
        if not rows:
            return []
        user_ids = [r[0] for r in rows]
        counts = {r[0]: r[1] for r in rows}
        users = self.env['res.users'].sudo().browse(user_ids)
        result = []
        for u in users:
            initials = ''.join(p[0] for p in (u.name or u.login).split()[:2]).upper()
            result.append({
                'id': u.id,
                'name': u.name,
                'login': u.login,
                'initials': initials or 'U',
                'count': counts.get(u.id, 0),
                'job': u.partner_id.function or '',
            })
        result.sort(key=lambda x: -x['count'])
        return result

    @api.model
    def inspect_user_access(self, user_id):
        """Return everything affecting a single user — for User Access Inspector panel."""
        user = self.env['res.users'].sudo().browse(int(user_id))
        if not user.exists():
            return {}

        today = Date.today()
        company = self.env.company
        base = [
            ('active_rule', '=', True),
            ('company_id', '=', company.id),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', today),
        ]
        user_rules = self.sudo().search(base + [
            ('responsible_user_ids', 'in', [user.id]),
            ('sh_restriction_type', '=', 'user'),
        ])
        group_rules = self.sudo().search(base + [
            ('responsible_group_ids', 'in', user.group_ids.ids),
            ('sh_restriction_type', '=', 'group'),
        ])
        all_rules = self._sh_filter_by_time(user_rules | group_rules)

        rules = []
        for r in all_rules:
            if r.sh_restriction_type == 'user':
                rtype = _('User')
            else:
                groups = r.responsible_group_ids.mapped('name')
                rtype = _('Group (%s)') % (', '.join(groups[:2]) or '—')
            if r.sh_restrict_by_time:
                status, expiry = 'time', '%.2f - %.2f' % (r.sh_time_from or 0.0, r.sh_time_to or 0.0)
            elif r.sh_expiry_date and (r.sh_expiry_date - today).days <= 7:
                status, expiry = 'expiring', r.sh_expiry_date.strftime('%Y-%m-%d')
            elif r.sh_expiry_date:
                status, expiry = 'active', r.sh_expiry_date.strftime('%Y-%m-%d')
            else:
                status, expiry = 'active', '—'
            rules.append({
                'id': r.id,
                'name': r.name or _('Unnamed Rule'),
                'type': rtype,
                'status': status,
                'expiry': expiry,
            })

        hidden_menus = all_rules.mapped('sh_hide_menu_ids')
        menus = [{'id': m.id, 'name': m.complete_name or m.name} for m in hidden_menus]

        field_rows = []
        for r in all_rules:
            for line in r.sh_field_access_line:
                for f in line.field_ids:
                    kinds = []
                    if line.invisible: kinds.append(_('Invisible'))
                    if line.readonly:  kinds.append(_('Readonly'))
                    if line.required:  kinds.append(_('Required'))
                    field_rows.append({
                        'model': line.model_id.model,
                        'field': f.name,
                        'kind': ', '.join(kinds) or _('Hidden'),
                    })

        effective_dict = self.get_access_restrictions({
            'user_id': user.id, 'company_id': company.id,
        }).get('model_restrictions', {})
        effective_pills = [self._sh_humanize_restriction(k) for k, v in effective_dict.items() if v]

        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'login': user.login,
            },
            'rules': rules,
            'menus': menus,
            'fields': field_rows,
            'effective': effective_pills,
            'counts': {
                'rules': len(rules),
                'menus': len(menus),
                'fields': len(field_rows),
                'effective': len(effective_pills),
            },
        }

    def _sh_humanize_restriction(self, key):
        labels = {
            'disable_developer_mode': _('Disable Developer Mode'),
            'global_hide_full_chatter': _('Hide Full Chatter'),
            'sh_readonly': _('Readonly Mode'),
            'global_hide_custom_filter': _('Hide Custom Filter'),
            'global_hide_custom_group_by': _('Hide Custom Group By'),
            'global_hide_filter': _('Hide Filter'),
            'global_hide_group_by': _('Hide Group By'),
            'global_hide_search_panel': _('Hide Search Panel'),
            'global_hide_spreadsheet': _('Hide Spreadsheet'),
            'sh_global_hide_field_credit_edit': _('Hide Create/Edit'),
            'sh_global_hide_favorite_edit': _('Hide Favorite Edit'),
            'sh_global_hide_favourite': _('Hide Favorite Menu'),
            'sh_global_hide_create': _('Hide Create'),
            'sh_global_hide_delete': _('Hide Delete'),
            'sh_global_hide_duplicate': _('Hide Duplicate'),
            'sh_global_hide_archive': _('Hide Archive'),
            'sh_global_hide_unarchive': _('Hide Unarchive'),
            'sh_restrict_xmlrpc': _('Restrict XML-RPC'),
        }
        return labels.get(key, key)

    def action_sh_cleanup_expired(self):
        """Quick action: deactivate all expired-but-still-active rules."""
        today = Date.today()
        to_archive = self.sudo().search([
            ('sh_expiry_date', '<', today),
            ('company_id', '=', self.env.company.id),
        ])
        count = len(to_archive)
        if count:
            to_archive.write({'active_rule': False})
            for r in to_archive:
                try:
                    r.message_post(
                        body=_("Auto-deactivated: rule expired on %s") % r.sh_expiry_date,
                        subtype_xmlid="mail.mt_note",
                    )
                except Exception:
                    _logger.warning("Could not post cleanup message for rule %s", r.id)
            self._sh_invalidate_caches()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cleanup Complete'),
                'message': _('%d expired rules deactivated. Restore via Filters → Inactive Rules.') % count if count
                           else _('No expired rules to deactivate.'),
                'type': 'success' if count else 'info',
                'sticky': False,
            },
        }

    def action_sh_refresh_cache(self):
        """Manual cache refresh — calls existing invalidation."""
        self._sh_invalidate_caches()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cache Refreshed'),
                'message': _('Access management cache invalidated successfully.'),
                'type': 'success',
                'sticky': False,
            },
        }

    @api.model
    def action_sh_open_dashboard(self):
        """Open the dashboard client action."""
        return {
            'type': 'ir.actions.client',
            'tag': 'sh_access_dashboard',
            'name': _('Access Dashboard'),
        }
