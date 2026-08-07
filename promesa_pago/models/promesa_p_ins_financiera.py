from odoo import fields,models,api

class PromesaPInsFinanciera(models.Model):
    _name = 'promesa.p.ins.financiera'

    name = fields.Char(
        string="Nombre",
    )
