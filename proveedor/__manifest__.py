{
    'name' : 'Proveedores - Fuentebuena',
    'summary' : 'Proveedores - Fuentebuena',
    'description' : "Módulo de proveedores de fuentebuena",
    'author': "Jorge Eduardo <jorge.limon@apreciafinanciera.com>",
    'version': "1.0",
    'depends': [
        'base',
        'contacts'
    ],
    'data': [
        'security/proveedor_security_groups.xml',
        'security/ir.model.access.csv',
        'wizard/proveedor_asignar_razon.xml',
        'data/proveedor_notificar_mail_template.xml',
        'views/proveedor_tipo_view.xml',
        'views/proveedor_res_partner_inherit_view.xml',
        'views/proveedor_menu.xml'
    ],
    'assets':{
      'web.assets_backend': [
          'proveedor/static/src/components/proveedor.js',
          'proveedor/static/src/js/validate.js',
      ]
    },
    'application': True,
    'installable': True,
}