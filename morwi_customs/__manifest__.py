# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Morwi Customs',
    'category': 'Contacts',
    'version': '19.0.0.0.0',
    'license': 'LGPL-3',
    'author': 'Morwi Encoders Consulting',
    'description': """
       This module adds related fields to the customer form.
        """,
    'summary': """
        This module adds related fields to the customer form.
        """,
    'depends': ['base', 'helpdesk', 'account', 'l10n_mx_edi', 'fleet', 'fleet_customer'],
    'data': [
        'security/security_view.xml',
        'views/res_partner_view.xml',
        'views/helpdesk_team_view.xml',
        'views/helpdesk_ticket_view.xml',
    ]
}