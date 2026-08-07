{
    'name': 'Fleet Tecno-Control',
    'summary': 'Fleet TecnoControl',
    'description': """Módulo para interacción entre Odoo y tecnocontrol""",
    'author': 'Jorge Eduardo Limon MUnguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
        'fleet',
        'atencion_cliente',
        'fleet_integracion_base'
    ],
    'data': [
        'data/ir_cron_asignar_gps.xml',
        'data/ir_cron_odometro_create.xml',
        'data/ir_cron_odometro_write.xml',
        'data/ir_cron_asginar_estado_bloqueo.xml',
        'security/ir.model.access.csv',
        'views/tecno_peticion_bloqueo_tipo_view.xml',
        'views/tecno_peticion_estado_view.xml',
        'views/fleet_tecno_peticion_respuesta_view.xml',
        'views/fleet_tecno_no_gps_view.xml',
        'views/fleet_tecno_peticion_bloqueo_view.xml',
        'views/fleet_tecno_actualizar_odometro_view.xml',
        'views/actualizar_odometro_etapa_view.xml',
        'views/tecno_inherit_ac_siniestro_view.xml',
        'views/fleet_tecnocontrol_menu.xml',
    ],
    'assets': {
      'web.assets_backend': [
          'fleet_tecnocontrol/static/src/components/mapa/mapa.js',
      ],
    },
    'auto_install': False,
    'application': True,
    'installable': True,
}