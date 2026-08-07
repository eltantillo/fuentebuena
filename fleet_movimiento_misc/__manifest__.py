{
    'name': 'Fleet Customer - Movimiento Misc',
    'version': '1.0',
    'category': 'Fleet',
    'description': 'Módulo personalizado para registrar los movimientos miscelaneos de los vehículos',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'fleet_customer',
        'municipio_mexico',
        'fleet'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/fleet_movimiento_pago.xml',
        'views/fleet_movimiento_misc_view.xml',
        'views/fleet_movimiento_misc_tipo_view.xml',
        'views/fleet_movimiento_misc_motivo_view.xml',
        'views/fleet_movimiento_misc_pago_view.xml',
        'views/fleet_movimiento_misc_etapa_view.xml',
        'views/fleet_movimiento_misc_fleet_view.xml',
        'views/fleet_movimiento_misc_menu.xml',
    ],
    'application': False,
    'installable': True
}