{
    "name": "XML Parse",
    "version": "1.0",
    "category": "XML",
    "summary": "Extraccion",
    "description": "Extracción de datos XML",
    "author": "Jorge Eduardo Limón Munguia <jorge.limon@fuentebuena.com>",
    "depends": [
        "base",
        "fleet_compra",
        "fleet_adecuacion"
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/xml_parse_inherit_fleet_view.xml',
        'wizard/alta_vehiculo_inherit.xml',
        'wizard/adecuacion.xml',
    ],
    "installable": True,
    "application": True,
}