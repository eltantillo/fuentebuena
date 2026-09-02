{
    'name': "Customer Portfolio 360",
    'version': '19.0.3.0.0',
    'category': 'Fleet',
    'summary': "Customer portfolio board and 360 client sheet for the leasing operation",
    'description': """
Customer Portfolio 360
======================

Two screens built as OWL client actions instead of standard views, because the
layout is a mockup agreed with the customer rather than a list/form:

* **Portfolio** — one row per customer with the risk semaphore, a KPI band,
  quick filters and search by customer, market or tax id.
* **Client 360** — the sheet behind each row: contract selector, leasing terms,
  collection and payment plan, tickets with their SLA clock, claim, operations,
  last interaction and the document file.

The rows live in `fleet.customer.portfolio` and the 360 payload is still a
scripted fixture. Both are stand-ins until the screens read `fleet_contrato`,
`fleet_poliza`, `fleet_siniestro`, `atencion_cliente` and `promesa_pago`; every
block in the sheet names the model it is expected to come from.
    """,
    'author': "Morwi Encoders Consulting",
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'cliente',
        'morwi_customs',
        'helpdesk',
        'fleet_contrato',
        'fleet_poliza',
        'fleet_siniestro',
        'fleet_tramite',
        'fleet_agenda_entrega',
        'atencion_cliente',
        'credito_arrendamiento',
        'whatsapp',
    ],
    'data': [
        'security/fleet_customer_portfolio_groups.xml',
        'views/fleet_customer_portfolio_actions.xml',
        'views/fleet_customer_portfolio_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_customer_portfolio/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True,
}
