{
    'name': 'Fleet Siniestro',
    'version': '1.0',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'description': 'Módulo de siniestro de pilotea',
    'depends': [
        'fleet_customer',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_siniestro_tipo_aseguradora_view.xml',
        'views/fleet_siniestro_inherit_fleet_.view.xml',
        'views/fleet_siniestro_estatus_view.xml',
        'views/fleet_siniestro_movilidad_view.xml',
        'views/fleet_siniestro_tipo_view.xml',
        'views/fleet_siniestro_fase_view.xml',
        'views/fleet_siniestro_etapa_view.xml',
        'views/fleet_siniestro_view.xml',
        'views/fleet_siniestro_renta_auxilio_track_view.xml',
        'views/fleet_siniestro_motivo_renta_view.xml',
        'views/fleet_siniestro_inherit_renta_view.xml',
        'views/renta_auxilio_tipo_view.xml',
        'wizard/renta_auxilio.xml',
        'wizard/terminar_renta_auxilio.xml',
        'views/fleet_siniestro_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_siniestro/static/src/components/timeline.js',
            'fleet_siniestro/static/src/scss/timeline.scss'
        ],
    },
    'application': False,
    'installable': True
}