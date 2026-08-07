{
    'name': 'Fleet - Gasto Operativo',
    'description': """Módulo para registrar los gastos operativos""",
    'author': 'Jorge Eduardo Limón MUnguia <jlimonmunguia@gmail.com>',
    'depends': [
        'fleet_customer',
        'base',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/gasto_operativo_metodo_pago_view.xml',
        'views/gasto_operativo_motivo_view.xml',
        'views/gasto_operativo_concepto_view.xml',
        'views/gasto_operativo_view.xml',
        'views/gasto_operativo_inherit_fleet_view.xml',
        'views/gasto_operativo_menu.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}