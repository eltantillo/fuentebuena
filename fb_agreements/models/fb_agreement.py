# -*- coding: utf-8 -*-
# Modelo Principal de Convenios (D-CONV-01) - Aprecia Financiera
from odoo import models, fields, api

class FbAgreement(models.Model):
    _name = 'fb.agreement'
    _description = 'Convenio'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Cabecera principal
    name = fields.Char(string='Denominación del Convenio', required=True, tracking=True)
    stage_id = fields.Many2one('fb.agreement.stage', string='Etapa', tracking=True, group_expand='_read_group_stage_ids')

    # Relaciones CRM y Contactos
    crm_lead_id = fields.Many2one('crm.lead', string='Oportunidad CRM')
    partner_id = fields.Many2one('res.partner', string='Dependencia / Empresa', required=True)
    contact_id = fields.Many2one('res.partner', string='Contacto Principal')
    phone = fields.Char(related='contact_id.phone', string='Teléfono', readonly=True)
    email = fields.Char(related='contact_id.email', string='Correo electrónico', readonly=True)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company)
    branch_id = fields.Many2one('fb.branch', string='Sucursal que atiende')
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    type_agreement = fields.Selection([('public', 'Publicos'),('private', 'Privados')], string='Tipo de convenio')

    # Bloque: Reglas Operativas
    fb_date_scheduled = fields.Date(string='Fecha agendada para revisión')
    fb_review_mode = fields.Selection([
        ('visit', 'Visita'),
        ('phone', 'Teléfono'),
        ('conference', 'Teleconferencia'),
        ('other', 'Otro')
    ], string='Forma de revisión')
    fb_date_survey = fields.Date(string='Fecha de levantamiento')
    fb_legal_representative = fields.Char(string='Representante Legal', help="Representante Legal")
    fb_union = fields.Char(string='Sindicato en colaboración', help='Sindicato en colaboración')
    fb_union_representative = fields.Char(string='Representante del Sindicato', help="Representante Representante del Sindicato")
    fb_union_attributions = fields.Text(string='Atribuciones del Sindicato')
    fb_amount_min_credit = fields.Float(string='Monto minimo del crédito')
    fb_borrowing_capacity = fields.Float(string='Capacidad de endeudamiento')
    fb_additional_borrowing_capacity = fields.Float(string='Capacidad de endeudamiento adicional')
    fb_registered_partner_id = fields.Many2one('res.partner', string='Razon social de la dependencia', help='Razon social de la dependencia')
    fb_contractual_powers = fields.Text(string='Atribuciones contratos', help='Atribuciones contratos por parte del sindicato')


    # Vigencias
    fb_contract_start_date = fields.Date(string='Inicio Vigencia Contrato')
    fb_contract_end_date = fields.Date(string='Fin Vigencia Contrato')
    fb_admin_start_date = fields.Date(string='Inicio Vigencia Administración')
    fb_admin_end_date = fields.Date(string='Fin Vigencia Administración')
    fb_credit_limit_start_date = fields.Date(string='Inicio Límite Créditos')
    fb_credit_limit_end_date = fields.Date(string='Fin Límite Créditos')

    # Estipulación y Validación
    fb_requires_stipulation = fields.Boolean(string='Requiere estipulación de descuento')
    fb_stipulation_send_mode = fields.Selection([
        ('digital', 'Digital'),
        ('physical', 'Físico')
    ], string='Forma de envío de estipulación')
    fb_total_employees = fields.Integer(string='Total de empleados')
    fb_validation_notes = fields.Text(string='Observaciones de validación')

    # Bloque: Ficha Técnica
    fb_business_type = fields.Char(string='Giro y antigüedad de la empresa')
    fb_main_activity = fields.Char(string='Actividad principal')
    fb_labor_indicators = fields.Text(string='Indicadores laborales', help='Indicadores laborales')
    fb_employee_count = fields.Integer(string='Número aprox. de trabajadores')
    fb_payment_period = fields.Selection([
        ('weekly', 'Semanal'),
        ('biweekly', 'Catorcenal'),
        ('semimonthly', 'Quincenal'),
        ('monthly', 'Mensual')
    ], string='Periodo de pago del sueldo')
    fb_competition = fields.Char(string='Competencia')
    fb_interest_rate = fields.Float(string='Tasa de Interés (%)')
    fb_commission_rate = fields.Float(string='Comisiones (%)')
    fb_insurance_rate = fields.Float(string='Seguro (%)')
    fb_additional_benefits = fields.Text(string='Beneficios adicionales')
    fb_added_value = fields.Text(string='Valor agregado')
    fb_contract_scope = fields.Text(string='Alcance del contrato')
    fb_payment_method = fields.Selection([
        ('transfer', 'Transferencia'),
        ('check', 'Cheque')
    ], string='Forma de Pago')
    fb_expected_result = fields.Text(string='Resultado esperado')
    responsible_cell_id = fields.Many2one('res.partner', string='Celula responsable', required=True)
    fb_product_credit_rate = fields.Float(string='Tasa de credito (Mensual/Anual)', help='Tasa de credito (Mensual/Anual)')
    fb_special_due_date = fields.Date(string='Fecha vencimiento especial', help='Fecha vencimiento especial/general')

    #Validacion
    fb_contact_credit_validation_id= fields.Many2one('res.partner', string='Contacto para validar créditos',
                                                     help='Contacto para validar créditos en trámite.' ,required=True)
    fb_accepted_means_validation_ids = fields.Many2many(
        'fb.accepted.means.validation',
        'fb_agreement_accepted_means_validation_rel',
        'agreement_id',
        'accepted_means_validation_id',
        string='Medios aceptados de validación.', help='Medios aceptados de validación')
    fb_authorized_signatures_letters_admission_ids= fields.One2many('fb.authorized.signatures.letters.admission', 'agreement_id',
                                                                    string='Firmas autorizadas en cartas de ingreso',
                                                                    help='Firmas autorizadas en cartas de ingreso')
    fb_validation_observations= fields.Text(string='Observaciones de validacion')

    # Lista descuento
    fb_discount_list_contact_id = fields.Many2one('res.partner', string='Contacto de listas de descuento.', help='Contacto de listas de descuento')
    fb_default_calendar= fields.Boolean(string='¿Existe calendario predeterminado?', help='¿Existe calendario predeterminado?')
    fb_payroll_closing_days_ids= fields.Many2many(
        'fb.payroll.closing.days',
        'fb_agreement_payroll_closing_days_rel',
        'agreement_id',
        'payroll_closing_days_id',
        string='Días de cierre de nómina', help='Días de cierre de nómina')

    fb_list_days_available_withholding= fields.Char(string='Días en que ya tienen disponible la lista de retenciones',
                                                    help='Días en que ya tienen disponible la lista de retenciones')
    fb_discount_list_submission_format= fields.Char(string='Formato para envío de listas de descuento a la dependencia',
                                                    help='Formato para envío de listas de descuento a la dependencia')
    fb_withholding_information_form= fields.Char(string='Formato en que la dependencia mandará la información de retenidos',
                                                 help='Formato en que la dependencia mandará la información de retenidos')

    # Pago
    payment_contact_id= fields.Many2one('res.partner', string='Contacto para revisar el pago', help='Contacto para revisar el pago')
    fb_payroll_agreement_payment_days_ids = fields.Many2many(
        'fb.payroll.agreement.payment.days',
        'fb_agreement_payroll_agreement_payment_days_rel',
        'agreement_id',
        'payroll_agreement_payment_days_id',
        string='Días en que paga el convenio la nómina al trabajador', help='Días en que paga el convenio la nómina al trabajador')
    available_days_payment_date= fields.Char(string='Días en que ya tienen disponible la fecha de pago',
                                                    help='Días en que ya tienen disponible la fecha de pago')
    agency_payment_bank_account_ids= fields.One2many('fb.agency.payment.bank.account', 'agreement_id', string='Cuenta de banco donde depositará la dependencia',
                                                     help='Cuenta de banco donde depositará la dependencia (Cuenta / CLABE)')
    fb_payment_observations_contract = fields.Text(string='Observaciones especiales del contrato', help='Observaciones especiales del contrato')

    # Relaciones de submodelos (líneas One2many)
    fb_eligibility_line_ids = fields.One2many('fb.agreement.eligibility', 'agreement_id', string='Elegibilidad de Empleados')
    fb_product_ids = fields.Many2many(
        'product.template',
        'fb_agreement_product_rel',
        'agreement_id',
        'product_id',
        string='Productos Pactados',
        domain=[('fb_available_in_agreements', '=', True)])
    fb_amount_line_ids = fields.One2many('fb.agreement.amount', 'agreement_id', string='Montos por Tipo de Empleado')
    fb_filter_line_ids = fields.One2many('fb.agreement.filter', 'agreement_id', string='Filtros de Originación')
    fb_deduction_line_ids = fields.One2many('fb.agreement.percep.deduc', 'agreement_id', string='Percepciones y Deducciones')
    fb_agreement_partner_ids = fields.One2many('fb.agreement.partner', 'agreement_id', string='Firma del convenio',
                                               help='Personas que apoyaron la firma del convenio')
    fb_signature_acknowledged_dependency_ids = fields.One2many('fb.signature.acknowledged.dependency', 'agreement_id', string='Firmas de enterado por la dependencia',
                                                   help='Firmas de enterado por la dependencia')
    fb_firms_aprecia_financiera_ids = fields.One2many('fb.firms.aprecia.financiera', 'agreement_id',
                                                               string='Firmas de aprecia financiera',
                                                               help='Firmas de aprecia financiera')
    fb_agreement_user_technical_specifications_ids = fields.One2many('fb.agreement.user.technical.specifications', 'agreement_id',
                                                                   string='Firmas',
                                                                   help='Firmas de ficha tenica')

    # Preconvenio
    # Participantes
    fb_applicant_id = fields.Many2one('res.users', string='Solicitante', help='Solicitante')
    fb_comptroller_validator_id = fields.Many2one('res.users', string='Validador Contraloría', help='Validador Contraloría')
    fb_executive_directorate_authorizer_id = fields.Many2one('res.users', string='Autorizador Dirección Ejecutiva Aprecia', help='Autorizador Dirección Ejecutiva Aprecia')
    fb_legal_approver_id = fields.Many2one('res.users', string='Autorizador Jurídico', help='Autorizador Jurídico Cobranza')
    fb_commercial_directorate_approver_id = fields.Many2one('res.users', string='Autorizador Dirección Comercial', help='Autorizador Dirección Comercial')
    fb_participant_observer_id = fields.Many2one('res.users', string='Participant / Observer', help='Participant / Observer')

    # Variables
    fb_format_type = fields.Selection([('layout_aprecia', 'Layout Aprecia'),
                                    ('layout_department', 'Layout dependencia')], string='Tipo de Formato', help='Tipo de Formato')
    fb_counterpart_id = fields.Many2one('res.partner', string='Contraparte', help='Contraparte')
    fb_counterparty_name = fields.Char(string='Denominación de la Contraparte', help='Denominación de la Contraparte')
    fb_personality = fields.Char(string='Personalidad (Acreditación 1)', help='Personalidad (Acreditación 1)')
    fb_personality_document = fields.Binary(string='Documento que Acredita Facultades (Acreditación 1)', help='Documento que Acredita Facultades (Acreditación 1)')
    fb_personality_ine = fields.Binary(string='Identificación (Acreditación 1)', help='Identificación (Acreditación 1)')
    fb_omission_accreditation = fields.Selection([
        ('yes', 'Si'),
        ('not', 'No')], string='¿Existe Omisión en la Acreditación o Documentación?',
        help='¿Existe Omisión en la Acreditación o Documentación?')
    fb_justification = fields.Char(string='Justificación', help='Justificación (en caso afirmativo)')
    fb_documentation_technical_data_sheet = fields.Selection([
        ('yes', 'Si'),
        ('not', 'No')], string='¿Se adjuntó documentación en la ficha técnica?',
        help='¿Se adjuntó documentación en la ficha técnica?')
    observations = fields.Text(string='Observaciones', help='Observaciones y/o Comentarios Generales para la Elaboración del Proyecto')

    documents_count = fields.Integer(string='Cantidad de Documentos', compute='_compute_documents_count')
    root_folder_id = fields.Many2one('documents.document', string='Carpeta raiz', help='Carpeta raiz')


    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['fb.agreement.stage'].search([])

    @api.depends('name', 'fb_date_survey')
    def _compute_documents_count(self):
        documents = self.env['documents.document']
        for record in self:
            record.documents_count = documents.search_count([('fb_agreement_id', '=', record.id)])

    def action_view_documents(self):
        self.ensure_one()
        return {
            'name': 'Documentos del convenio',
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'kanban,list',
            'domain': [('fb_agreement_id', '=', self.id)],
            'context':{
                'default_fb_agreement_id': self.id,
                'searchpanel_default_folder_id': self.root_folder_id.id,},
        }