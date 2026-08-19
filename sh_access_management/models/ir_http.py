# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import models, _
from odoo.http import request
from odoo.exceptions import AccessDenied
from odoo.fields import Date


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        user = request.env.user
        if not user or user._is_public():
            return result

        restrictions = request.env['sh.access.manager'].sudo().get_access_restrictions({
            'user_id': user.id,
            'company_id': request.env.company.id
        })

        result['sh_is_readonly'] = restrictions.get('model_restrictions', {}).get('sh_readonly', False)
        return result

    @classmethod
    def _authenticate(cls, endpoint):
        """ Intercept XMLRPC requests and block users with sh_restrict_xmlrpc. """
        result = super()._authenticate(endpoint)

        try:
            path = request.httprequest.environ.get('PATH_INFO', '')
            if not path.startswith('/xmlrpc/'):
                return result

            uid = request.env.uid
            if not uid:
                return result

            user = request.env['res.users'].sudo().browse(uid)
            if not user or user._is_public() or user.has_group('base.group_system') or user.has_group('sh_access_management.sh_access_management_manager'):
                return result

            user_domain = [
                ('responsible_user_ids', 'in', [uid]),
                ('active_rule', '=', True),
                ('sh_restrict_xmlrpc', '=', True),
                '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
                ('sh_restriction_type', '=', 'user'),
                ('company_id', '=', request.env.company.id),
            ]
            group_domain = [
                ('responsible_group_ids', 'in', user.group_ids.ids),
                ('active_rule', '=', True),
                ('sh_restrict_xmlrpc', '=', True),
                '|', ('sh_expiry_date', '=', False), ('sh_expiry_date', '>=', Date.today()),
                ('sh_restriction_type', '=', 'group'),
                ('company_id', '=', request.env.company.id),
            ]

            access_records = (
                request.env['sh.access.manager'].sudo().search(user_domain) |
                request.env['sh.access.manager'].sudo().search(group_domain)
            )
            access_records = request.env['sh.access.manager'].sudo()._sh_filter_by_time(access_records)

            if access_records:
                raise AccessDenied(
                    _("XML-RPC / Script access is restricted for your account. "
                      "Please contact the Administrator for further assistance."))
        except AccessDenied:
            raise
        except Exception:
            pass

        return result
