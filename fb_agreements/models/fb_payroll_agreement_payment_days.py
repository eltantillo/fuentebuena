# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FbPayrollAgreementPaymentDays(models.Model):
    _name = 'fb.payroll.agreement.payment.days'
    _description = 'Días en que paga el convenio la nómina al trabajador'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(string='Activo', default=True)