# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FbAgencyPaymentBankAccount(models.Model):
    _name='fb.agency.payment.bank.account'
    _description = 'Cuenta de banco donde depositará la dependencia'

    bank = fields.Char(string='Banco', required=True)
    bank_account = fields.Char(string='Cuenta banco', required=True)
    key_account = fields.Char(string='Cuenta clave')
    bank_reference = fields.Char(string='Referencia bancaria')
    method_payment_id= fields.Many2one('l10n_mx_edi.payment.method', string='Como realizara el pago',
                                       help='Como realizara el pago')
    observations_contract = fields.Text(string='Observaciones del contacto', help='Observaciones del contacto')
    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')