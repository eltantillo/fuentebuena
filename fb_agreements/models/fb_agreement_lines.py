# -*- coding: utf-8 -*-
# Submodelos para las líneas repetibles del Convenio
from odoo import models, fields

class FbAgreementEligibility(models.Model):
    _name = 'fb.agreement.eligibility'
    _description = 'Elegibilidad de Empleados'

    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')
    fb_employee_type_id = fields.Many2one('fb.employee.type', string='Tipo de Empleado', required=True)
    fb_employee_count = fields.Integer(string='Número de Empleados')

class FbAgreementProduct(models.Model):
    _name = 'fb.agreement.product'
    _description = 'Productos Pactados por Convenio'

    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Producto', required=True)
    fb_rate = fields.Float(string='Tasa de Crédito (%)')
    fb_payment_frequency = fields.Selection([
        ('weekly', 'Semanal'),
        ('biweekly', 'Catorcenal'),
        ('semimonthly', 'Quincenal'),
        ('monthly', 'Mensual')
    ], string='Frecuencia de Pago')
    fb_min_term = fields.Integer(string='Plazo Mínimo')
    fb_max_term = fields.Integer(string='Plazo Máximo')
    fb_min_amount = fields.Monetary(string='Monto Mínimo', currency_field='currency_id')
    fb_max_amount = fields.Monetary(string='Monto Máximo', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='agreement_id.currency_id')

class FbAgreementAmount(models.Model):
    _name = 'fb.agreement.amount'
    _description = 'Montos de Crédito por Tipo de Empleado'

    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')
    name = fields.Char(string='Descripción', required=True)
    fb_employee_type_id = fields.Many2one('fb.employee.type', string='Tipo de Empleado', required=True)
    fb_qty_employee = fields.Integer(string='Cantidad de empleados')
    fb_min_amount = fields.Monetary(string='Monto Mínimo', currency_field='currency_id')
    fb_max_amount = fields.Monetary(string='Monto Máximo', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='agreement_id.currency_id')

class FbAgreementFilter(models.Model):
    _name = 'fb.agreement.filter'
    _description = 'Filtros del Sistema de Créditos'

    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')
    fb_route_convenio = fields.Char(string='RUTA (Convenio)')
    fb_group_dependency = fields.Char(string='GRUPO (Dependencia)')
    fb_region_area = fields.Char(string='REGIÓN (Área)')
    fb_activity_type = fields.Char(string='ACTIVIDAD (Tipo empleado)')
    fb_population_municipality = fields.Char(string='POBLACIÓN (Municipio)')

class FbAgreementPercepDeduc(models.Model):
    _name = 'fb.agreement.percep.deduc'
    _description = 'Percepciones y Deducciones para Capacidad de Pago'

    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')
    fb_line_type = fields.Selection([
        ('perception', 'Percepción'),
        ('deduction', 'Deducción')
    ], string='Tipo', required=True)
    fb_code = fields.Char(string='Clave', required=True)
    fb_concept = fields.Char(string='Concepto', required=True)
    fb_notes = fields.Text(string='Observaciones')
