# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import fields, models, api, _


class ShConditionalDomain(models.Model):
    _name = "sh.conditional.domain"
    _description = "Conditional Domain"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sh_access_manager_id = fields.Many2one(
        "sh.access.manager", string="Access Manager", ondelete='cascade', tracking=True)

    sh_model_id = fields.Many2one(
        'ir.model', string="Model", required=True, ondelete='cascade', tracking=True,
        domain="[('model', '!=', 'sh.access.manager')]")
    sh_model_name = fields.Char(related="sh_model_id.model", string="Model Name", store=True)

    sh_conditional_readonly = fields.Boolean("Read Only", tracking=True)
    sh_conditional_create = fields.Boolean("Create", tracking=True)
    sh_conditional_update = fields.Boolean("Update", tracking=True)
    sh_conditional_delete = fields.Boolean("Delete", tracking=True)
    #### REPLACE STOP #### 
    @api.onchange('sh_conditional_readonly')
    def _onchange_sh_conditional_readonly(self):
        """If Read Only is enabled, auto-check all create, update, delete, and action restrictions."""
        if self.sh_conditional_readonly:
            self.sh_conditional_create = True
            self.sh_conditional_update = True
            self.sh_conditional_delete = True
            self.sh_conditional_action = True

    @api.onchange('sh_conditional_create', 'sh_conditional_update', 'sh_conditional_delete', 'sh_conditional_action')
    def _onchange_sh_conditional_crud(self):
        """If any CRUD or Action restriction is disabled, uncheck Read Only."""
        if not self.sh_conditional_create or not self.sh_conditional_update or not self.sh_conditional_delete or not self.sh_conditional_action:
            self.sh_conditional_readonly = False

    sh_conditional_domain = fields.Char("Condition", tracking=True)

    sh_conditional_action = fields.Boolean("Action", tracking=True)
    sh_conditional_print = fields.Boolean("Print", tracking=True)
    sh_conditional_filter = fields.Boolean("Filter", tracking=True)
    sh_conditional_group_by = fields.Boolean("Group By", tracking=True)
    sh_conditional_favourite = fields.Boolean("Favorite", tracking=True)
    sh_conditional_search_panel = fields.Boolean("Search Panel", tracking=True)


    # ─── Auto-check Read when any CRUD operation is enabled ──────────────────
    @api.onchange('sh_conditional_create', 'sh_conditional_update', 'sh_conditional_delete')
    def _onchange_crud_auto_read(self):
        """Read must always be enabled if any other CRUD restriction is active.
        A user cannot be restricted from editing/creating records they cannot see."""
        for rec in self:
            if rec.sh_conditional_create or rec.sh_conditional_update or rec.sh_conditional_delete:
                rec.sh_conditional_readonly = True

    # ─── Warn if same model already exists in Model Access tab ───────────────
    @api.onchange('sh_model_id')
    def _onchange_model_conflict_warning(self):
        """Warn admin if the same model is already configured in the Model Access tab.

        Priority Order (low → high override):
        Conditional Domain → Field Access → Model Access → Global

        Conditional rules will still apply on top, but the admin should be aware."""
        for rec in self:
            if rec.sh_model_id and rec.sh_access_manager_id:
                existing_model_line = rec.sh_access_manager_id.sh_access_model_line.filtered(
                    lambda l: l.model_id == rec.sh_model_id
                )
                if existing_model_line:
                    return {
                        'warning': {
                            'title': _("Model Already Configured in Model Access Tab"),
                            'message': _(
                                "The model '%s' already has restrictions in the 'Model Access' tab.\n\n"
                                "Priority: Global > Model Access > Field Access > Conditional Domain.\n\n"
                                "Conditional rules will still apply but note that Global and Model Access "
                                "restrictions take precedence. If Model Access already hides 'Create' for "
                                "ALL records, this conditional rule will not add anything further."
                            ) % rec.sh_model_id.name,
                        }
                    }

    @api.model_create_multi
    def create(self, vals_list):
        """Create conditional domain records and invalidate access caches."""
        res = super().create(vals_list)
        self.env['sh.access.manager']._sh_invalidate_caches()
        return res

    def write(self, vals):
        """Write conditional domain records and invalidate access caches."""
        res = super().write(vals)
        self.env['sh.access.manager']._sh_invalidate_caches()
        return res

    def unlink(self):
        """Unlink conditional domain records and invalidate access caches."""
        res = super().unlink()
        self.env['sh.access.manager']._sh_invalidate_caches()
        return res

    def action_open_domain_form(self):
        """Open the standalone domain builder popup for this conditional rule."""
        view_id = self.env.ref('sh_access_management.sh_conditional_domain_popup_form_view').id
        return {
            'name': 'Define Conditions',
            'type': 'ir.actions.act_window',
            'res_model': 'sh.conditional.domain',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': self.env.context
        }

    @api.model
    def sh_check_record_matches_rules(self, model_name, res_id, rules):
        """Check if a specific record matches any of the given conditional domain rules.

        Called from the frontend FormController to evaluate per-record button visibility.
        Returns a dict indicating which CRUD buttons should be hidden for this record.

        Args:
            model_name (str): Technical model name, e.g. 'sale.order'.
            res_id (int): The ID of the record currently open in the form.
            rules (list[dict]): List of rule dicts from check_crud_operation, each with:
                - domain (str): Odoo domain string, e.g. "[('partner_id.name','=','Azure Interior')]"
                - apply_filter (bool): Whether this rule has a domain filter.
                - conditional_action (bool): Whether to hide the Action menu.
                - conditional_print (bool): Whether to hide the Print menu.
            (Note: conditional_create / conditional_update / conditional_delete come from sh_conditional_* fields
             which are already merged into global ir.rule domains on the backend.)

        Returns:
            dict: { conditional_create: bool, conditional_update: bool, conditional_delete: bool }
        """
        result = {'hide_create': False, 'hide_write': False, 'hide_delete': False, 'hide_archive': False, 'hide_unarchive': False, 'hide_action': False, 'hide_print': False, 'hide_filter': False, 'hide_group_by': False, 'hide_favourite': False, 'hide_search_panel': False, 'hide_search_bar': False}

        if not model_name or not res_id or not rules:
            return result

        try:
            Model = self.env[model_name].sudo()
        except KeyError:
            return result

        from odoo.tools.safe_eval import safe_eval
        from odoo.osv import expression



        for rule in rules:
            domain_str = rule.get('domain')
            has_domain = bool(domain_str)

            if has_domain:
                # ── Domain set → check if this specific record matches ────────────────────
                # Works for both apply_filter=True and apply_filter=False (domain takes priority)
                try:
                    domain_list = safe_eval(domain_str, {})
                    full_domain = expression.AND([[('id', '=', int(res_id))], domain_list])

                    match_count = Model.search_count(full_domain)


                    if match_count > 0:
                        is_readonly = rule.get('readonly')
                        if rule.get('hide_create') or is_readonly:
                            result['hide_create'] = True
                        if rule.get('hide_write') or is_readonly:
                            result['hide_write'] = True
                        if (rule.get('hide_delete') or is_readonly):
                            result['hide_delete'] = True
                        if rule.get('hide_archive'):
                            result['hide_archive'] = True
                        if rule.get('hide_unarchive'):
                            result['hide_unarchive'] = True
                        if rule.get('hide_action'):
                            result['hide_action'] = True
                        if rule.get('hide_print'):
                            result['hide_print'] = True
                        if rule.get('hide_filter'):
                            result['hide_filter'] = True
                        if rule.get('hide_group_by'):
                            result['hide_group_by'] = True
                        if rule.get('hide_favourite'):
                            result['hide_favourite'] = True
                        if rule.get('hide_search_panel'):
                            result['hide_search_panel'] = True
                except Exception as e:

                    continue
            else:
                # ── No domain → ALL records of this model are restricted ─────────────────
                # apply_filter=False + no domain: applies to every record
                is_readonly = rule.get('readonly')
                if rule.get('hide_create') or is_readonly:
                    result['hide_create'] = True
                if rule.get('hide_write') or is_readonly:
                    result['hide_write'] = True
                if (rule.get('hide_delete') or is_readonly):
                    result['hide_delete'] = True
                if rule.get('hide_archive'):
                    result['hide_archive'] = True
                if rule.get('hide_unarchive'):
                    result['hide_unarchive'] = True
                if rule.get('hide_action'):
                    result['hide_action'] = True
                if rule.get('hide_print'):
                    result['hide_print'] = True
                if rule.get('hide_filter'):
                    result['hide_filter'] = True
                if rule.get('hide_group_by'):
                    result['hide_group_by'] = True
                if rule.get('hide_favourite'):
                    result['hide_favourite'] = True
                if rule.get('hide_search_panel'):
                    result['hide_search_panel'] = True


        return result
