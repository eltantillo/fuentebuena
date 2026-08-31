# -*- coding: utf-8 -*-
{
    'name': 'Convenios - Aprecia Financiera',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Módulo de gestión de convenios, reglas operativas y ficha técnica (D-CONV-01)',
    'description': """
        Módulo D-CONV-01: Gestión centralizada de Convenios para Aprecia Financiera.
        - Integración con CRM (crm.lead)
        - Reglas Operativas y Ficha Técnica
        - Pre-Convenio y Configuración del Sistema de Créditos
    """,
    'author': 'Morwi Encoders Consulting',
    'depends': ['base', 'crm', 'product', 'resource', 'l10n_mx_edi', 'documents'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/fb_accepted_means_validation_data.xml',
        'data/fb_payroll_closing_days_data.xml',
        'data/fb_payroll_agreement_payment_days_data.xml',
        'data/fb_integration_log_data.xml',
        'views/fb_employee_type_views.xml',
        'views/fb_agreement_stage_views.xml',
        'views/fb_agreement_views.xml',
        'views/product_template_views.xml',
        'views/res_company_views.xml',
        'views/crm_lead_views.xml',
        'views/fb_instance_views.xml',
        'views/fb_integration_log_views.xml',
        'views/documents_document_views.xml',
        'views/fb_menu_views.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'fb_agreements/static/src/components/**/*',
            ],
        },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
