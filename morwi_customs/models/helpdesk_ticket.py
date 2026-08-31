# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api

TIPO_TICKET_SELECTION = [
    ('comercial', 'Comercial'),
    ('cobranza_prorrogas', 'Cobranza y prórrogas'),
    ('mantenimiento', 'Mantenimiento'),
    ('robos_siniestros', 'Robos y siniestros'),
    ('gestoria_vehicular', 'Gestoría vehicular'),
    ('geocerca', 'Geocerca'),
    ('facturacion', 'Facturación'),
    ('gps', 'GPS'),
    ('promociones', 'Promociones'),
    ('terminaciones_contrato', 'Terminaciones de contrato'),
    ('otros', 'Otros'),
]


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    tipo_ticket = fields.Selection(selection=TIPO_TICKET_SELECTION, string='Tipo de ticket')
    motivo_id = fields.Many2one(
        comodel_name='helpdesk.ticket.motivo', string='Motivo',
        domain="[('tipo_ticket', '=', tipo_ticket)]")
    nivel_escalamiento = fields.Selection(selection=[
        ('nivel_1', 'Nivel 1 - Responsable operativo'),
        ('nivel_2', 'Nivel 2 - Gerente nacional'),
        ('nivel_3', 'Nivel 3 - Dirección'),
    ], string='Nivel de escalamiento')

    sales_representative_id = fields.Many2one(comodel_name='res.users', string='Sales representative')
    fleet_customer_plaza_id = fields.Many2one(comodel_name='fleet.customer.plaza', string='Square')
    fleet_customer_producto_id = fields.Many2one(comodel_name='fleet.customer.producto', string='Contract type')
    fleet_vehicle_id = fields.Many2one(string='Vehicle', comodel_name='fleet.vehicle')
    odometer = fields.Float(string='Kilometrage', related='fleet_vehicle_id.odometer')
    fleet_vehicle_log_contract_id = fields.Many2one(
        comodel_name='fleet.vehicle.log.contract', string='Contract')
    license_plate = fields.Char(related='fleet_vehicle_id.license_plate', string='License Plate')
    vin_sn = fields.Char(related='fleet_vehicle_id.vin_sn', string='VIN')
    fleet_siniestro_id = fields.Many2one(comodel_name='fleet.siniestro', string='Related Claim')
    #Razón social -> res.partner (estándar Odoo)
    #Régimen fiscal -> res.partner — localización fiscal MX (l10n_mx)
    #Uso CFDI -> account.move / res.partner — localización fiscal MX (l10n_mx)
    #Tipo de contrato -> fleet.customer.producto (vía fleet.vehicle.log.contract.producto_id)
    #Unidad asignada -> fleet.vehicle
    # CAMPOS DEL CLIENTE
    phone_number = fields.Char(related='partner_id.phone')
    rfc = fields.Char(related='partner_id.vat')
    # CAMPOS NUEVOS
    specific_request = fields.Text(string='Specific Request')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    date = fields.Date(string='Date')
    bank_id = fields.Many2one(comodel_name='res.bank', string='Bank')
    reference_cie = fields.Char(string='Reference / CIE')
    issue_description = fields.Text(string='Service / Issue Description')
    location = fields.Text(string='Location')
    event_datetime = fields.Datetime(string='Date / Time / Location')
    event_narrative = fields.Text(string='Event Narrative')
    origin_destination = fields.Char(string='Origin / Destination')
    reason = fields.Text(string='Reason')
    app_trip = fields.Char(string='App / Trip')
    requested_period = fields.Date(string='Requested Period')
    referral_code = fields.Char(string='Referral Code / ID')
    promotion = fields.Selection(selection=[('option_1', 'Option 1'),('option_2', 'Option 2')], string='Promotion')
    customer_intent = fields.Text(string='Customer Intent')

    # === Team-gated additional fields ===
    # Selection fields marked "placeholder options" below use a generic
    # pending/in_process/resolved list until the real business options are defined.
    # GNV
    gnv_next_ruling_date = fields.Date(string='Next GNV Ruling Date')
    # Delivery
    tentative_delivery_date = fields.Date(string='Tentative Delivery Date')
    # Impound Lot
    pound_exit_date = fields.Date(string='Impound Lot Exit Date')
    # Claim
    claim_status = fields.Selection(selection=[('pending', 'Pending'), ('in_process', 'In Process'), ('resolved', 'Resolved')], string='Claim Status')
    # General Follow-up
    tracking_log = fields.Text(string='Follow-up Log')
    advisor_id = fields.Many2one(comodel_name='res.users', string='Advisor / Sales Rep Involved')
    info_evidence = fields.Binary(string='Evidence of Information Provided')
    capture_evidence = fields.Binary(string='Evidence / Screenshot (if applicable)')
    # Payment
    payment_voucher_id = fields.Many2one(comodel_name='account.payment', string='Payment Voucher')
    extension_folio = fields.Char(string='Extension Folio (if applicable)')
    # Service / Issue
    customer_availability = fields.Selection(selection=[('pending', 'Pending'), ('in_process', 'In Process'), ('resolved', 'Resolved')], string='Customer Availability')
    photos_video_evidence = fields.Binary(string='Photos / Video (if applicable)')
    # Accident
    accident_photos = fields.Binary(string='Photos')
    insurance_authority_report = fields.Char(string='Insurance / Authority Report Folio')
    gps_location = fields.Char(string='GPS Location (if applicable)')
    # Procedure
    procedure_document = fields.Binary(string='Procedure Document / Folio')
    fine_evidence = fields.Binary(string='Fine / Verification / Policy Evidence')
    # Trip
    trip_duration = fields.Char(string='Duration')
    debt_claim_extension_validation = fields.Char(string='Debt / Claim / Extension Validation')
    # Fiscal Data (mirrored read-only from the customer)
    legal_name = fields.Char(related='partner_id.name', string='Legal Name (Razón social)', readonly=True)
    fiscal_zip = fields.Char(related='partner_id.zip', string='Zip Code', readonly=True)
    fiscal_regime = fields.Selection(related='partner_id.l10n_mx_edi_fiscal_regime', string='Fiscal Regime', readonly=True)
    fiscal_usage = fields.Selection(related='partner_id.l10n_mx_edi_usage', string='CFDI Usage', readonly=True)
    fiscal_proof_document = fields.Binary(string='Fiscal Proof / Data Document')
    # Referral / Promotion
    delivery_evidence_date = fields.Date(string='Delivery Date / Communication Evidence')
    # Contract
    contract_end_date = fields.Date(string='Contract End Date')
    balance_amount = fields.Monetary(string='Balance / Status Amount', currency_field='currency_id')
    # Case Closure
    case_status_confirmed = fields.Boolean(string='Case Status Confirmed to Customer')
    payment_management_result = fields.Selection(selection=[('pending', 'Pending'), ('in_process', 'In Process'), ('resolved', 'Resolved')], string='Payment Management Result')
    final_response_sent = fields.Boolean(string='Final Response Sent to Customer')
    closed_stage_id = fields.Many2one(comodel_name='helpdesk.stage', string='Ticket Closed Stage')
    # Billing Correction
    invoice_corrected = fields.Boolean(string='Invoice / Complement Corrected')
    correction_commitment_date = fields.Date(string='Correction Commitment Date Communicated')
    closure_evidence = fields.Binary(string='Closure Evidence Uploaded (Portal/Email)')
    corrected_info_channel = fields.Selection(selection=[('pending', 'Pending'), ('in_process', 'In Process'), ('resolved', 'Resolved')], string='Corrected Info or Channeled to Responsible')
    commercial_responsible_notified = fields.Boolean(string='Commercial Responsible Notified')
    procedure_validated = fields.Boolean(string='Procedure Validated')
    response_instruction_document = fields.Binary(string='Response Instruction / Document Sent to Customer')
    # Benefit
    follow_up_responsible_id = fields.Many2one(comodel_name='res.users', string='Follow-up Responsible')
    benefit_validated = fields.Boolean(string='Benefit Validated')
    benefit_request_result = fields.Selection(selection=[('pending', 'Pending'), ('in_process', 'In Process'), ('resolved', 'Resolved')], string='Benefit Request Result')
    benefit_rejection_reason = fields.Text(string='Benefit Rejection Reason')
    # Termination
    termination_requirements_confirmed = fields.Boolean(string='Termination Requirements Confirmed')
    termination_next_step = fields.Text(string='Termination Next Step Communicated')
    # Maintenance
    maintenance_appointment_datetime = fields.Datetime(string='Maintenance Appointment Confirmed')
    diagnosis_confirmed = fields.Boolean(string='Diagnosis Confirmed')
    customer_informed_status = fields.Boolean(string='Customer Informed of Status / Next Step')
    # Geofence
    geofence_authorization = fields.Selection(selection=[('approved', 'Approved'), ('rejected', 'Rejected')], string='Geofence Authorization')
    conditions_communicated = fields.Boolean(string='Conditions Communicated to Customer')

    # === Visibility gates mirrored from helpdesk.ticket.motivo ===
    show_gnv_next_ruling_date = fields.Boolean(related='motivo_id.show_gnv_next_ruling_date')
    show_tentative_delivery_date = fields.Boolean(related='motivo_id.show_tentative_delivery_date')
    show_pound_exit_date = fields.Boolean(related='motivo_id.show_pound_exit_date')
    show_claim_status = fields.Boolean(related='motivo_id.show_claim_status')
    show_tracking_log = fields.Boolean(related='motivo_id.show_tracking_log')
    show_advisor_id = fields.Boolean(related='motivo_id.show_advisor_id')
    show_info_evidence = fields.Boolean(related='motivo_id.show_info_evidence')
    show_specific_request = fields.Boolean(related='motivo_id.show_specific_request')
    show_capture_evidence = fields.Boolean(related='motivo_id.show_capture_evidence')
    show_payment_voucher_id = fields.Boolean(related='motivo_id.show_payment_voucher_id')
    show_amount = fields.Boolean(related='motivo_id.show_amount')
    show_date = fields.Boolean(related='motivo_id.show_date')
    show_bank_id = fields.Boolean(related='motivo_id.show_bank_id')
    show_reference_cie = fields.Boolean(related='motivo_id.show_reference_cie')
    show_extension_folio = fields.Boolean(related='motivo_id.show_extension_folio')
    show_issue_description = fields.Boolean(related='motivo_id.show_issue_description')
    show_location = fields.Boolean(related='motivo_id.show_location')
    show_customer_availability = fields.Boolean(related='motivo_id.show_customer_availability')
    show_photos_video_evidence = fields.Boolean(related='motivo_id.show_photos_video_evidence')
    show_event_datetime = fields.Boolean(related='motivo_id.show_event_datetime')
    show_event_narrative = fields.Boolean(related='motivo_id.show_event_narrative')
    show_accident_photos = fields.Boolean(related='motivo_id.show_accident_photos')
    show_insurance_authority_report = fields.Boolean(related='motivo_id.show_insurance_authority_report')
    show_gps_location = fields.Boolean(related='motivo_id.show_gps_location')
    show_procedure_document = fields.Boolean(related='motivo_id.show_procedure_document')
    show_fleet_customer_plaza_id = fields.Boolean(related='motivo_id.show_fleet_customer_plaza_id')
    show_fine_evidence = fields.Boolean(related='motivo_id.show_fine_evidence')
    show_origin_destination = fields.Boolean(related='motivo_id.show_origin_destination')
    show_reason = fields.Boolean(related='motivo_id.show_reason')
    show_trip_duration = fields.Boolean(related='motivo_id.show_trip_duration')
    show_app_trip = fields.Boolean(related='motivo_id.show_app_trip')
    show_debt_claim_extension_validation = fields.Boolean(related='motivo_id.show_debt_claim_extension_validation')
    show_legal_name = fields.Boolean(related='motivo_id.show_legal_name')
    show_fiscal_zip = fields.Boolean(related='motivo_id.show_fiscal_zip')
    show_fiscal_regime = fields.Boolean(related='motivo_id.show_fiscal_regime')
    show_fiscal_usage = fields.Boolean(related='motivo_id.show_fiscal_usage')
    show_fiscal_proof_document = fields.Boolean(related='motivo_id.show_fiscal_proof_document')
    show_requested_period = fields.Boolean(related='motivo_id.show_requested_period')
    show_referral_code = fields.Boolean(related='motivo_id.show_referral_code')
    show_promotion = fields.Boolean(related='motivo_id.show_promotion')
    show_delivery_evidence_date = fields.Boolean(related='motivo_id.show_delivery_evidence_date')
    show_fleet_customer_producto_id = fields.Boolean(related='motivo_id.show_fleet_customer_producto_id')
    show_contract_end_date = fields.Boolean(related='motivo_id.show_contract_end_date')
    show_balance_amount = fields.Boolean(related='motivo_id.show_balance_amount')
    show_customer_intent = fields.Boolean(related='motivo_id.show_customer_intent')
    show_fleet_vehicle_id = fields.Boolean(related='motivo_id.show_fleet_vehicle_id')
    show_case_status_confirmed = fields.Boolean(related='motivo_id.show_case_status_confirmed')
    show_payment_management_result = fields.Boolean(related='motivo_id.show_payment_management_result')
    show_final_response_sent = fields.Boolean(related='motivo_id.show_final_response_sent')
    show_closed_stage_id = fields.Boolean(related='motivo_id.show_closed_stage_id')
    show_invoice_corrected = fields.Boolean(related='motivo_id.show_invoice_corrected')
    show_correction_commitment_date = fields.Boolean(related='motivo_id.show_correction_commitment_date')
    show_closure_evidence = fields.Boolean(related='motivo_id.show_closure_evidence')
    show_corrected_info_channel = fields.Boolean(related='motivo_id.show_corrected_info_channel')
    show_commercial_responsible_notified = fields.Boolean(related='motivo_id.show_commercial_responsible_notified')
    show_procedure_validated = fields.Boolean(related='motivo_id.show_procedure_validated')
    show_response_instruction_document = fields.Boolean(related='motivo_id.show_response_instruction_document')
    show_follow_up_responsible_id = fields.Boolean(related='motivo_id.show_follow_up_responsible_id')
    show_benefit_validated = fields.Boolean(related='motivo_id.show_benefit_validated')
    show_benefit_request_result = fields.Boolean(related='motivo_id.show_benefit_request_result')
    show_benefit_rejection_reason = fields.Boolean(related='motivo_id.show_benefit_rejection_reason')
    show_termination_requirements_confirmed = fields.Boolean(related='motivo_id.show_termination_requirements_confirmed')
    show_termination_next_step = fields.Boolean(related='motivo_id.show_termination_next_step')
    show_maintenance_appointment_datetime = fields.Boolean(related='motivo_id.show_maintenance_appointment_datetime')
    show_diagnosis_confirmed = fields.Boolean(related='motivo_id.show_diagnosis_confirmed')
    show_customer_informed_status = fields.Boolean(related='motivo_id.show_customer_informed_status')
    show_geofence_authorization = fields.Boolean(related='motivo_id.show_geofence_authorization')
    show_conditions_communicated = fields.Boolean(related='motivo_id.show_conditions_communicated')

    @api.onchange('tipo_ticket')
    def _onchange_tipo_ticket(self):
        if self.motivo_id and self.motivo_id.tipo_ticket != self.tipo_ticket:
            self.motivo_id = False

    @api.onchange('fleet_vehicle_id')
    def _onchange_fleet_vehicle_id(self):
        if self.fleet_vehicle_id and not self.partner_id and self.fleet_vehicle_id.driver_id:
            self.partner_id = self.fleet_vehicle_id.driver_id
        if self.fleet_siniestro_id and self.fleet_siniestro_id.vehiculo_id != self.fleet_vehicle_id:
            self.fleet_siniestro_id = False

    @api.onchange('fleet_vehicle_log_contract_id')
    def _onchange_fleet_vehicle_log_contract_id(self):
        contract = self.fleet_vehicle_log_contract_id
        if not contract:
            return
        self.fleet_vehicle_id = contract.vehicle_id
        self.fleet_customer_plaza_id = contract.plaza_id
        self.fleet_customer_producto_id = contract.producto_id
        if not self.partner_id:
            self.partner_id = contract.cliente_id

    @api.onchange('partner_id')
    def _onchange_partner_id_contract(self):
        contract = self.fleet_vehicle_log_contract_id
        if contract and self.partner_id and contract.cliente_id != self.partner_id:
            self.fleet_vehicle_log_contract_id = False

