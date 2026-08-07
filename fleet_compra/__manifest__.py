{
    "name": "Fleet Compra",
    "version": "1.0",
    "category": "Fleet",
    "summary": "Fleet Compra",
    "description": "Fleet Compra",
    "depends": [
        "base",
        "fleet",
        "fleet_customer",
        "proveedor",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/fleet_compra_sequence.xml",
        "data/fleet_compra_reporte.xml",
        "reports/report_action_compra.xml",
        "views/fleet_compra_inherit_vehicle.xml",
        "views/fleet_compra_categoria_view.xml",
        "views/fleet_compra_condicion_view.xml",
        "views/fleet_compra_etapa_view.xml",
        "views/fleet_orden_compra_line_view.xml",
        "views/fleet_orden_compra_view.xml",
        'wizard/alta_vehiculo_view.xml',
        "views/fleet_compra_menu.xml"
    ],
    'assets':{
        'web.report_assets_common': [
            'fleet_compra/static/src/img/icon.png'
        ]
    },
    "installable": True,
    "application": True,
}

