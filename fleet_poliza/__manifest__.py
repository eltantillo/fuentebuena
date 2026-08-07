{
    'name': 'Fleet Customer - Polizas',
    'version': '1.0',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'description': 'Módulo personalizado para registrar las polizas para los vehículos',
    'depends': [
        'fleet_customer',
        'fleet',
        "proveedor",
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_poliza_view.xml',
        'views/fleet_poliza_tipo_cobertura_view.xml',
        'views/fleet_poliza_tipo_valor_view.xml',
        'views/fleet_poliza_fleet_view.xml',
        'views/fleet_poliza_tipo_view.xml',
        'views/fleet_poliza_config_view.xml',
        'views/fleet_poliza_menu.xml',
    ],
    'application': False,
    'installable': True
}