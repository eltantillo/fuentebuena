{
    'name': 'Fleet Customer - Recepción',
    'version': '18.0',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'description': 'Módulo personalizado para registrar las recepciones de los vehículos',
    'depends': [
        'fleet_customer',
        'web',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_recepcion_invoice_view.xml',
        'views/fleet_recepcion_view.xml',
        'views/fleet_recepcion_lugar_view.xml',
        'views/fleet_recepcion_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_recepcion/static/src/components/recepcion.js',
            'fleet_recepcion/static/src/components/alta_vehiculo.xml',
            'fleet_recepcion/static/src/components/valorar_vehiculo.xml',
            'fleet_recepcion/static/src/components/recepcion.xml',
            'fleet_recepcion/static/src/scss/recepcion.scss',
        ],
    },
    'application': False,
    'installable': True
}