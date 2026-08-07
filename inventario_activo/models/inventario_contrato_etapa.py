from odoo import fields,models,api


class InventarioContratoEtapa(models.Model):
    _name = "inventario.contrato.etapa"

    name = fields.Char(
        string="Nombre"
    )