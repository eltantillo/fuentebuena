{
    'name': 'Pilotea - Portal',
    'version': '1.0',
    'author': 'Jorge Eduardo Limón Munguia <jlimonmunguia@gmail.com>',
    'description': """Módulo de acceso a clientes""",
    'depends': [
        'web',
        'website',
        'base',
        'fleet_poliza',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'templates/portal_template.xml',
        'views/portal_track_poliza_view.xml',
        'views/portal_track_menu.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_app/static/src/components/portal_main/portal_main.xml',
            'portal_app/static/src/components/portal_main/login.xml',
            'portal_app/static/src/components/portal_main/home.xml',
            'portal_app/static/src/components/portal_main/portal_main.js',
        ],
    },
    'application': False,
    'installable': True
}