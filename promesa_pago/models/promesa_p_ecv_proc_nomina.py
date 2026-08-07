from odoo import fields,models,api


class PromesaPEcvProcNomina(models.Model):
    _name = 'promesa.p.ecv.proc.nomina'

    name = fields.Char(
        string="Nombre"
    )