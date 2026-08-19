# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Crédito y Arrendamiento',
    'category': 'Accounting',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Morwi Encoders Consulting',
    'summary': """
        Créditos de arrendamiento con su tabla de amortización y planes de pago, ligados al contacto.
        """,
    'description': """
        Modela los créditos de arrendamiento (renta) de un cliente, con su
        tabla de amortización semanal y sus planes de pago cuando existan.
        Se conecta a res.partner mediante un botón inteligente. Pensado para
        poblarse desde un sistema externo a través de la API estándar de Odoo.
        """,
    'depends': ['base', 'mail', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'views/credito_arrendamiento_view.xml',
        'views/credito_arrendamiento_plan_pago_view.xml',
        'views/res_partner_view.xml',
        'views/credito_arrendamiento_menu.xml',
    ],
    'installable': True,
    'application': False,
}
