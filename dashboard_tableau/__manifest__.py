{
    'name': "Dashboard tableau",
    'description': "Modulo de conexión de tableros tableau con odoo",
    'author': "Jorge Eduardo <jorge.limon@apreciafinanciera.com>",
    'version': "1.0",
    'depends': ['base',
                'web',
                'website'],
    'data': [
        'security/security_groups.xml',
        'views/dashboard_tableau_action.xml',
        'views/dashboard_tableau_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dashboard_tableau/static/src/css/style.css',
            'dashboard_tableau/static/src/components/dashboard_tableau.js',
            'dashboard_tableau/static/src/components/dashboard_tableau.xml',
        ],
    },
    'application': True,
    'installable': True,
}