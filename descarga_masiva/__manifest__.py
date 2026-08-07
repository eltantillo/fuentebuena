{
    'name': 'Descargas masivas',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'version': '1.0',
    'depends':[
        'base',
        'fleet_customer',
        'fleet_poliza'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/descarga_masiva.xml',
        'views/descarga_masiva_menu.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}