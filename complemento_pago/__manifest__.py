{
    'name': 'Complementos de pago',
    'version': '1.0',
    'description': """ Modúlo para gestionar los complementos de pago""",
    'depends': [
        'base',
        'fleet_customer',
        'fleet_adecuacion',
        'fleet_poliza',
        'fleet_tramite',
        'fleet_mantenimiento'
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/complemento_inherit_adecuacion_view.xml',
        'views/complemento_inherit_fleet_view.xml',
        'views/complemento_inherit_mantenimiento_view.xml',
        'views/complemento_inherit_poliza_view.xml',
        'views/complemento_inherit_tramite_view.xml',
        'views/complento_pago_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}