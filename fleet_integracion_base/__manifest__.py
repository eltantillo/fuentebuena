{
    "name": "Integración GPS Global",
    "version": "1.0",
    "category": "Fleet",
    "summary": "Itegración telemetría",
    "description": "Base para poder añadir funcionamiento con telemetría",
    "author": "Jorge Eduardo Limón Munguia <jorge.limon@fuentebuena.com>",
    "depends": [
        "base",
        "fleet_customer"
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/integracion_base_inherit_fleet_view.xml',
        'views/integracion_base_bloqueo_view.xml',
        'wizard/peticion_bloqueo.xml',
        'views/integracion_base_menu.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_integracion_base/static/src/components/mapa/mapa.js',
        ],
    },
    "installable": True,
    "application": True,
}