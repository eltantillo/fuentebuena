{
    'name': 'Empleados - Extensión',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Modificaciones en el módelo de empleados',
    'description': 'Modificaciones en el modelo de empleados',
    'depends': ['base', 'hr', 'fleet_customer'],
    'data': [
        'views/hr_work_inherit_view.xml',
    ],
    'installable': True,
    'application': True,
}