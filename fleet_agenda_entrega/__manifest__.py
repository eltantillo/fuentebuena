{
    'name': 'Fleet Agenda Entrega',
    'description': 'Módulo para agendar las entregas de vehiculos',
    'version': '1.0',
    'author': 'Jorge Eduardo Limón Munguia <jorge.limon@fuentebuena.com>',
    'depends': [
        'base',
        'fleet_customer',
        'fleet_tramite',
        'fleet',
        'hr',
        'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/agenda_entrega_mail_template.xml',
        'data/agenda_entrega_actualizacion_mail_template.xml',
        'data/agenda_entrega_deposito_valido.xml',
        'views/agenda_entrega_view.xml',
        'views/agenda_entrega_estatus_dictamen_view.xml',
        'views/agenda_entrega_dictamen_view.xml',
        'views/agenda_entrega_canalizacion_view.xml',
        'views/agenda_entrega_estatus_instrumentacion_view.xml',
        'views/agenda_entrega_etapa_view.xml',
        'views/agenda_entrega_lugar_view.xml',
        'views/agenda_entrega_tipo_evento_view.xml',
        'views/agenda_entrega_estatus_comprobante_view.xml',
        'views/agenda_entrega_estatus_evento_view.xml',
        'views/agenda_entrega_evento_view.xml',
        'wizard/evento.xml',
        'wizard/solventar.xml',
        'wizard/evidencia.xml',
        'views/agenda_entrega_menu.xml'
    ],
    'assets': {
      'web.assets_backend': [
          'fleet_agenda_entrega/static/src/css/style.css',
      ]
    },
    'application': True,
    'installable': True,
}