{
    'name': 'Fleet Customer - Tramites',
    'version': '1.0',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'description': 'Módulo personalizado para registrar los tramites de los vehículos',
    'depends': [
        'fleet_customer',
        'base',
        'web',
        'hr'
    ],
    'data': [
        'data/tramite_vencimiento_cron.xml',
        'security/ir.model.access.csv',
        'views/fleet_tramite_motivo_pago_view.xml',
        'views/fleet_tramite_tipo_view.xml',
        'views/fleet_tramite_view.xml',
        'views/fleet_tramite_fleet_view.xml',
        'views/fleet_tramite_config_view.xml',
        'views/fleet_tramite_menu.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_tramite/static/src/components/hybrid_field/hybrid_field.js',
        ],
    },
    'application': True,
    'installable': True
}