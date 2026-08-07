{
    'name': 'Fleet Customer - Odómetros',
    'version': '1.0',
    'summary': 'Módulo personalizado para registrar los odómetros para los vehículos',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'fleet',
        'fleet_customer',
        'fleet_tecnocontrol',
        'fleet_mantenimiento',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/fleet_odometro_view.xml',
        'views/odometro_inherit_fleet_view.xml',
        'wizard/actualizar_odometro.xml'
    ],
    'application': False,
    'installable': True
}