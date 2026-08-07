{
    'name' : 'Gestión de caído',
    'summary' : 'Gestión de proceso de caídos',
    'description' : "Módulo de para gestiones",
    'author': "Jorge Eduardo <jorge.limon@fuentebuena.com>",
    'version': "1.0",
    'depends': [
        'base',
        'fleet_customer',
        'fleet_tecnocontrol',
        'fleet_mantenimiento',
        'web',
        'hr'
    ],
    'data': [
        'data/gc_notificacion_mail_template.xml',
        'data/gc_confirmar_recepcion_cron.xml',
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'wizard/gc_retencion.xml',
        'wizard/gc_liberar_retencion.xml',
        'views/gestion_caido_track_view.xml',
        'views/gestion_caido_inherit_fleet_view.xml',
        'views/gestion_caido_estado_view.xml',
        'views/gestion_caido_view.xml',
        'views/gc_invoice_posesion.xml',
        'views/gc_razon_cancel_view.xml',
        'views/gestion_caido_gestor_view.xml',
        'views/gestion_caido_menu.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'gestion_caido/static/src/components/posesion.js',
            'gestion_caido/static/src/components/posesion.xml',
        ],
    },
    'application': True,
    'installable': True,
}