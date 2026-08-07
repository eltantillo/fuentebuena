{
    'name': 'Fleet Customer - Catalogos',
    'version': '1.0',
    'category': 'Fleet',
    'description': 'Módulo personalizado para registrar los catalogos generales',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'fleet_poliza',
        'fleet_customer',
        'fleet_tramite',
        'fleet_mantenimiento',
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_catalogo_orig_creacion_view.xml',
        'views/fleet_catalogo_frecuencia_pago_view.xml',
        'views/fleet_catalogo_frecuencia_herencia_view.xml',
        'views/fleet_catalogo_org_creacion_herencia_view.xml',
        'views/fleet_catalogo_dependencia_view.xml',
        'views/fleet_catalogo_dependencia_herencia_view.xml',
        'views/fleet_catalogo_menu.xml'
    ],
    'application': False,
    'installable': True
}