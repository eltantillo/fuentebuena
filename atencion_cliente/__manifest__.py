{
    'name': 'Atención al cliente',
    'version': '18.0',
    'category': 'Fleet',
    'description': 'Módulo para registrar las interacciones de atención al cliente',
    'author': 'Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
        'fleet_customer',
        'fleet_siniestro',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/atencion_cliente_sequence.xml',
        'data/atencion_cliente_siniestro_mail_template.xml',
        'views/atencion_cliente_responsabilidad_view.xml',
        'views/atencion_cliente_interaccion_view.xml',
        'views/atencion_cliente_incidencia_view.xml',
        'views/atencion_cliente_siniestro_view.xml',
        'views/atencion_cliente_caracteristica.xml',
        'views/atencion_cliente_incidencia_ps_view.xml',
        'views/atencion_cliente_geocerca_view.xml',
        'views/atencion_cliente_status_registro_view.xml',
        'views/atencion_cliente_causa_incidencia_ps_view.xml',
        'views/atencion_cliente_causa_incidencia_view.xml',
        'views/atencion_cliente_interaccion_stage_view.xml',
        'views/atencion_cliente_medio_contacto_view.xml',
        'views/atencion_cliente_tipo_solicitud_view.xml',
        'views/atencion_cliente_menu.xml'
    ],
    'application': True,
    'installable': True,
}