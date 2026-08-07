{
    'name': 'Promesa de pago',
    'summary': 'Promesa de pago migración',
    'description': """ Módulo dedicado a promesas de pago """,
    'author': 'Jorge Eduardo Limón Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
        'hr',
        'mail'
    ],
    'data':[
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/promesa_p_celula_view.xml',
        'views/promesa_p_convenio_view.xml',
        'views/promesa_p_ecv_proc_nomina_view.xml',
        'views/promesa_p_ecv_promesa_pago_view.xml',
        'views/promesa_p_estado_cumplimiento_view.xml',
        'views/promesa_p_frecuencia_nomina_view.xml',
        'views/promesa_p_ins_financiera_view.xml',
        'views/promesa_p_zona_view.xml',
        'views/promesa_p_rol_view.xml',
        'views/promesa_p_proyeccion_cobranza_view.xml',
        'views/promesa_p_periodo_nom_convenio_view.xml',
        'views/promesa_p_promesa_view.xml',
        'views/promesa_p_pago_view.xml',
        'views/promesa_p_menu.xml'
    ],
    'application': True,
    'installable':True,
    'auto_install':False,
}