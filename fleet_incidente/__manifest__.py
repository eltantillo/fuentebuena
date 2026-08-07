{
    'name': 'Fleet Incidente',
    'version': '1.0',
    'description': """Módulo para registrar los incidentes""",
    'author': 'Jorge Eduardo Limón MUnguia <jlimonmunguia@gmail.com>',
    'depends': [
        'fleet_customer',
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_incidente_tipo_view.xml',
        'views/fleet_incidente_view.xml',
        'views/fleet_incidente_menu.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}