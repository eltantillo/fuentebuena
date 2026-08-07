{
    'name': 'Facturas - Fuentebuena',
    'description': 'Módulo exlusivo para temas de facturación',
    'version': '1.0',
    'depends': [
        'base',
        'account',
        'product_unspsc',
        'product',
        'l10n_mx_edi',
    ],
    'data': [
        'security/factura_security_groups.xml',
        'security/ir.model.access.csv',
        'views/factura_account_move_lines_view.xml',
        'views/factura_modelo_vin_view.xml',
        'views/factura_account_move_list_inherit.xml',
        'views/factura_dashboard_invoice_view.xml',
        'views/factura_motivo_cancelacion.xml',
        'views/factura_modal_informativo_view.xml',
        'views/factura_monto_autorizado_view.xml',
        'views/factura_account_move_line_inherit.xml',
        'views/factura_unspsc_categoria_view.xml',
        'views/factura_contabilidad_inherit.xml',
        'views/factura_menus.xml'
    ],
    'assets':{
      'web.assets_backend': [
          'factura/static/src/components/dashboard.js',
          'factura/static/src/components/dashboard.xml',
          'factura/static/lib/chart/chart.js',
      ],
    },
    'application': True,
    'installable': True,
}