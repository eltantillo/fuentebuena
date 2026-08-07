{
    "name": "Integración GPS Samsara",
    "version": "1.0",
    "category": "Fleet",
    "summary": "Itegración telemetría con Samsara",
    "description": "Base para poder añadir funcionamiento con telemetría usando el proveedor de GPS Samsara",
    "author": "Jorge Eduardo Limón Munguia <jorge.limon@fuentebuena.com>",
    "depends": [
        "base",
        "fleet_customer",
        "fleet_integracion_base"
    ],
    "data": [
        'data/fleet_samsara_gps_cron.xml',
        'data/fleet_samsara_ubicacion_cron.xml',
        'data/fleet_samsara_odo_create_cron.xml',
        'data/fleet_samsara_odo_update_cron.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": True,
}