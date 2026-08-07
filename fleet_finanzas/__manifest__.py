{
    'name': 'Fleet Finanzas',
    'version': '1.0',
    'category': 'Fleet',
    'description': 'Módulo para vistas ',
    'author': 'Jorge Eduardo Limon Munguia  <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
        'fleet',
        'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_finanza_inherit_fleet.xml',
        'views/fleet_finanza_linea_credito_view.xml',
        'views/fleet_finanza_sesionario_view.xml',
        'views/fleet_finanza_fuente_fondeo_view.xml',
        'wizard/fleet_finanza_asignar.xml',
        'views/fleet_finanza_menu.xml',
    ],
    'application': False,
    'installable': True
}