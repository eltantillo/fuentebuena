from odoo import models, fields, _
from odoo.fields import Date
from odoo.exceptions import AccessDenied
from odoo.http import request


class ResUsers(models.Model):
    """
        A class to manage the access of users.
    """
    _inherit = 'res.users'

    # Disable login for users who are restricted from login
    def _check_credentials(self, credential, env):
        """ Extends authentication check by verifying if the user is restricted from login. """
        user_id = self.env.user.id
        user = self.env.user

        # Bypass all restrictions for system administrators
        if user.has_group('base.group_system') or user.has_group('sh_access_management.sh_access_management_manager'):
            return super()._check_credentials(credential, env)

        user_domain = [
            ('responsible_user_ids', 'in', [user_id]),
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('sh_restriction_type', '=', 'user'),
            ('company_id', '=', self.env.company.id)
        ]
        group_domain = [
            ('responsible_group_ids', 'in', user.group_ids.ids),
            ('active_rule', '=', True),
            '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
            ('sh_restriction_type', '=', 'group'),
            ('company_id', '=', self.env.company.id)
        ]
        access_records = self.env['sh.access.manager'].sudo().search(user_domain) | self.env['sh.access.manager'].sudo().search(group_domain)

        # Apply time-based filter: only keep rules whose time window is currently active
        access_records = self.env['sh.access.manager'].sudo()._sh_filter_by_time(access_records)

        if any(access_records.mapped('sh_disable_user_login')):
            raise AccessDenied(
                _("Your login has been temporarily Restricted. "
                  "Please contact the Administrator for further assistance."))

        # Block XML-RPC / script access if restricted.
        # interactive=False means this is an API/script call (execute_kw).
        # interactive=True means browser login — allow it through.
        if any(access_records.mapped('sh_restrict_xmlrpc')):
            is_script_call = not env.get('interactive', True)
            if is_script_call:
                raise AccessDenied(
                    _("XML-RPC / Script access is restricted for your account. "
                      "Please contact the Administrator for further assistance."))

        return super()._check_credentials(credential, env)
