{
    'name': "Mapa interactivo",
    'description': "Mapa para marketing",
    'author': "Jorge Eduardo <jorge.limon@apreciafinanciera.com>",
    'version': "1.0",
    'depends': ['base',
                'web',
                'website'],
    'data': [
        'templates/mapa_interactivo_template.xml',
    ],
    'assets':{
        'web.assets_backend': [],
        'web.assets_frontend': [
        ],
        'formulario.assets_frontend': [
            'mapa/static/src/css/style.css',
            'mapa/static/src/css/bootstrap.min.css',
        ]
    },
    'application': True,
    'installable': True,
}