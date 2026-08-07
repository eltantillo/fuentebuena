{
    'name': 'Extensión usuarios',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'User',
    'description': """MOdulo para expandir la funcionalidad de un usuario""",
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
        'fleet_customer',
        'fleet_agenda_entrega'
    ],
    'data': [
        'views/inherit_user_view.xml',
        'views/inherit_agenda_entrega_view.xml',
    ],
    'application': False,
    'installable': True,
}