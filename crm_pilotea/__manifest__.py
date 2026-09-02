# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CRM - Originación Pilotea',
    'category': 'Sales/CRM',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Morwi Encoders Consulting',
    'summary': """
        Campos del flujo de originación de Pilotea en el CRM, alimentados por
        el Sistema de Originación.
        """,
    'description': """
        Agrega a crm.lead los campos del embudo de originación de Pilotea, de
        lead registrado a cliente activo, con los nombres técnicos que usa el
        conector en su payload JSON. Todo el bloque se oculta mientras Pilotea
        no esté entre las empresas activas.
        """,
    'depends': ['crm', 'fleet', 'fleet_customer', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_etiqueta_view.xml',
        'views/res_company_view.xml',
        'views/crm_lead_view.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
