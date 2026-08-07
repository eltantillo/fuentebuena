{
    'name': 'Fleet Customer - Adecuaciones',
    'version': '18.0',
    'category': 'Fleet',
    'summary': 'Módulo personalizado complemento de fleet_customer',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'fleet_customer',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_adecuacion_catalogo_view.xml',
        'views/fleet_adecuacion_view.xml',
        'views/fleet_adecuacion_fleet_view.xml',
        'views/fleet_adecuacion_config_view.xml',
        'views/fleet_adecuacion_menu.xml',
    ],
    'application': False,
    'installable': True,
}