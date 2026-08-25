{
    'name': 'Expediente de vehículos',
    'version': '1.0',
    'category': 'Fleet',
    'summary': 'Módulo personalizado complemento de fleet_customer',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
        'fleet_customer',
        'fleet_tramite',
        'fleet_adecuacion',
        'hr'
    ],
    'data': [
        'data/expediente_alerta_cron.xml',
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/expediente_tipo_view.xml',
        'views/expediente_config_tipo_view.xml',
        'views/expediente_action.xml',
        'views/expediente_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'expediente/static/src/components/expediente.js',
            'expediente/static/src/components/expediente.xml',
            'expediente/static/src/scss/expediente.scss',
        ],
    },
    'application': False,
    'installable': True,
}