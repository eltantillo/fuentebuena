# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields

from .helpdesk_ticket import TIPO_TICKET_SELECTION


class HelpdeskTicketMotivo(models.Model):
    _name = 'helpdesk.ticket.motivo'
    _description = 'Motivo de ticket'
    _order = 'tipo_ticket, sequence, name'

    name = fields.Char(string='Motivo', required=True)
    tipo_ticket = fields.Selection(selection=TIPO_TICKET_SELECTION, string='Tipo de ticket', required=True)
    sequence = fields.Integer(string='Secuencia', default=10)
    active = fields.Boolean(string='Activo', default=True)

    _name_tipo_uniq = models.Constraint(
        'unique(name, tipo_ticket)',
        'Ya existe un motivo con ese nombre para este tipo de ticket.',
    )

    # Each field below gates the visibility of the matching helpdesk.ticket
    # field in the "Additional Info" tab: unchecked = hidden for this motivo.
    # GNV
    show_gnv_next_ruling_date = fields.Boolean(string='Show: Next GNV Ruling Date')
    # Delivery
    show_tentative_delivery_date = fields.Boolean(string='Show: Tentative Delivery Date')
    # Impound Lot
    show_pound_exit_date = fields.Boolean(string='Show: Impound Lot Exit Date')
    # Claim
    show_claim_status = fields.Boolean(string='Show: Claim Status')
    # General Follow-up
    show_tracking_log = fields.Boolean(string='Show: Follow-up Log')
    show_advisor_id = fields.Boolean(string='Show: Advisor / Sales Rep Involved')
    show_info_evidence = fields.Boolean(string='Show: Evidence of Information Provided')
    show_specific_request = fields.Boolean(string='Show: Specific Request')
    show_capture_evidence = fields.Boolean(string='Show: Evidence / Screenshot (if applicable)')
    # Payment
    show_payment_voucher_id = fields.Boolean(string='Show: Payment Voucher')
    show_amount = fields.Boolean(string='Show: Amount')
    show_date = fields.Boolean(string='Show: Date')
    show_bank_id = fields.Boolean(string='Show: Bank')
    show_reference_cie = fields.Boolean(string='Show: Reference / CIE')
    show_extension_folio = fields.Boolean(string='Show: Extension Folio (if applicable)')
    # Service / Issue
    show_issue_description = fields.Boolean(string='Show: Service / Issue Description')
    show_location = fields.Boolean(string='Show: Location')
    show_customer_availability = fields.Boolean(string='Show: Customer Availability')
    show_photos_video_evidence = fields.Boolean(string='Show: Photos / Video (if applicable)')
    # Accident
    show_event_datetime = fields.Boolean(string='Show: Date / Time / Location')
    show_event_narrative = fields.Boolean(string='Show: Event Narrative')
    show_accident_photos = fields.Boolean(string='Show: Photos')
    show_insurance_authority_report = fields.Boolean(string='Show: Insurance / Authority Report Folio')
    show_gps_location = fields.Boolean(string='Show: GPS Location (if applicable)')
    # Procedure
    show_procedure_document = fields.Boolean(string='Show: Procedure Document / Folio')
    show_fleet_customer_plaza_id = fields.Boolean(string='Show: Square')
    show_fine_evidence = fields.Boolean(string='Show: Fine / Verification / Policy Evidence')
    # Trip
    show_origin_destination = fields.Boolean(string='Show: Origin / Destination')
    show_reason = fields.Boolean(string='Show: Reason')
    show_trip_duration = fields.Boolean(string='Show: Duration')
    show_app_trip = fields.Boolean(string='Show: App / Trip')
    show_debt_claim_extension_validation = fields.Boolean(string='Show: Debt / Claim / Extension Validation')
    # Fiscal Data
    show_legal_name = fields.Boolean(string='Show: Legal Name (Razón social)')
    show_fiscal_zip = fields.Boolean(string='Show: Zip Code')
    show_fiscal_regime = fields.Boolean(string='Show: Fiscal Regime')
    show_fiscal_usage = fields.Boolean(string='Show: CFDI Usage')
    show_fiscal_proof_document = fields.Boolean(string='Show: Fiscal Proof / Data Document')
    # Referral / Promotion
    show_requested_period = fields.Boolean(string='Show: Requested Period')
    show_referral_code = fields.Boolean(string='Show: Referral Code / ID')
    show_promotion = fields.Boolean(string='Show: Promotion')
    show_delivery_evidence_date = fields.Boolean(string='Show: Delivery Date / Communication Evidence')
    # Contract
    show_fleet_customer_producto_id = fields.Boolean(string='Show: Contract type')
    show_contract_end_date = fields.Boolean(string='Show: Contract End Date')
    show_balance_amount = fields.Boolean(string='Show: Balance / Status Amount')
    show_customer_intent = fields.Boolean(string='Show: Customer Intent')
    # Case Closure
    show_fleet_vehicle_id = fields.Boolean(string='Show: Vehicle')
    show_case_status_confirmed = fields.Boolean(string='Show: Case Status Confirmed to Customer')
    show_payment_management_result = fields.Boolean(string='Show: Payment Management Result')
    show_final_response_sent = fields.Boolean(string='Show: Final Response Sent to Customer')
    show_closed_stage_id = fields.Boolean(string='Show: Ticket Closed Stage')
    # Billing Correction
    show_invoice_corrected = fields.Boolean(string='Show: Invoice / Complement Corrected')
    show_correction_commitment_date = fields.Boolean(string='Show: Correction Commitment Date Communicated')
    show_closure_evidence = fields.Boolean(string='Show: Closure Evidence Uploaded (Portal/Email)')
    show_corrected_info_channel = fields.Boolean(string='Show: Corrected Info or Channeled to Responsible')
    show_commercial_responsible_notified = fields.Boolean(string='Show: Commercial Responsible Notified')
    show_procedure_validated = fields.Boolean(string='Show: Procedure Validated')
    show_response_instruction_document = fields.Boolean(string='Show: Response Instruction / Document Sent to Customer')
    # Benefit
    show_follow_up_responsible_id = fields.Boolean(string='Show: Follow-up Responsible')
    show_benefit_validated = fields.Boolean(string='Show: Benefit Validated')
    show_benefit_request_result = fields.Boolean(string='Show: Benefit Request Result')
    show_benefit_rejection_reason = fields.Boolean(string='Show: Benefit Rejection Reason')
    # Termination
    show_termination_requirements_confirmed = fields.Boolean(string='Show: Termination Requirements Confirmed')
    show_termination_next_step = fields.Boolean(string='Show: Termination Next Step Communicated')
    # Maintenance
    show_maintenance_appointment_datetime = fields.Boolean(string='Show: Maintenance Appointment Confirmed')
    show_diagnosis_confirmed = fields.Boolean(string='Show: Diagnosis Confirmed')
    show_customer_informed_status = fields.Boolean(string='Show: Customer Informed of Status / Next Step')
    # Geofence
    show_geofence_authorization = fields.Boolean(string='Show: Geofence Authorization')
    show_conditions_communicated = fields.Boolean(string='Show: Conditions Communicated to Customer')
