# -*- coding: utf-8 -*-
##############################################################################
#                 @author IT Admin
#
##############################################################################

{
    'name': 'CFDI Retenciones',
    'version': '19.1.1',
    'description': ''' Agrega campos para generar CFDI de Retenciones e Información de Pagos
    ''',
    'category': 'Accounting',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'account', 'l10n_mx_edi',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/reason_cancelation_sat_view.xml',
        'reports/invoice_report.xml',
        'views/factura_retencion_view.xml',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/ret.xml',
	],
    'application': False,
    'installable': True,
}
