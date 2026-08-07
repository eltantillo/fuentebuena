{
    'name': "Calculadora",
    'description': "Calculadora de crédito",
    'author': "Jorge Eduardo <jorge.limon@apreciafinanciera.com>",
    'version': "1.0",
    'depends': ['base',
                'web',
                'website'],
    'data': [
        'templates/calculadora_template.xml',
    ],
    'assets':{
        'web.assets_backend': [],
        'web.assets_frontend': [
        ],
        'calculadora.assets_frontend': [
            'calculadora/static/src/css/style.css',
            'calculadora/static/src/css/bootstrap.min.css',
        ]
    },
    'application': True,
    'installable': True,
}