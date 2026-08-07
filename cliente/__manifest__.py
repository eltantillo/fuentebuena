{
    'name': 'Clientes - Pilotea',
    'version': '1.0',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'description': 'Módulo de clientes de pilotea',
    'depends': [
        'base',
        'contacts',
        'fleet'
    ],
    'data': [
        'views/cliente_inherit.xml',
        'views/cliente_inherit_res_partner_view.xml',
        'views/cliente_inherit_fleet.xml',
        'views/cliente_menu.xml',
    ],
    'application': True,
    'installable': True
}