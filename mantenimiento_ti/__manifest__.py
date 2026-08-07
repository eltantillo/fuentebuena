{
    'name': 'Mantenimiento Ti',
    'version': '1.0',
    'category': 'Mantenimiento',
    'summary': 'Mantenimiento Ti',
    'description': """Modulo para mantenimiento de TI""",
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mantenimiento_cat_actividad_view.xml',
        'views/mantenimiento_cat_proy_sistema_view.xml',
        'views/mantenimiento_cat_servicio_prov_view.xml',
        'views/mantenimiento_gasto_ti_etapa_view.xml',
        'views/mantenimiento_preventivo_etapa_view.xml',
        'views/mantenimiento_ti_proveedor_view.xml',
        'views/mantenimiento_ti_menu.xml'
    ],
    'application': True,
    'installable': True,
}