{
    'name': 'Fleet Customer - Mantenimientos',
    'version': '1.0',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'description': 'Módulo personalizado para registrar los mantenimientos para los vehículos',
    'depends': [
        'fleet_customer',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_mantenimiento.xml',
        'views/fleet_mantenimiento_inherit_fleet_view.xml',
        'views/fleet_mantenimiento_servicio_tipo_view.xml',
        'views/fleet_mantenimiento_unidad_medida_view.xml',
        'views/fleet_mantenimiento_etapa_view.xml',
        'views/fleet_mantenimiento_tipo_view.xml',
        'views/fleet_mantenimiento_servicio_view.xml',
        'views/fleet_mantenimiento_view.xml',
        'views/fleet_mantenimiento_categoria_view.xml',
        'views/fleet_mantenimiento_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_mantenimiento/static/src/components/semaforo/semaforo.js',
        ],
    },
    'application': False,
    'installable': True
}