from odoo import models, api, fields


class XMLParseInheritFleet(models.Model):
    _inherit = "fleet.vehicle"

    xml_factura = fields.Binary(
        string="XML de factura",
        tracking=True
    )

    def ventana_importar(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "adecuacion",
            "name": "Alta adecuación",
            "view_mode": "form",
            "target": "new",
            "view_id": self.env.ref("xml_parse.adecuacion_view_form").id,
            "context": {'default_vehiculo_id': self.id},
        }