# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api

# Las claves técnicas de las selecciones van en inglés minúscula: el JSON del
# conector manda la clave, nunca la etiqueta, para que ni los acentos ni los
# espacios entren al payload.
APP_SELECTION = [
    ('uber', 'Uber'),
    ('didi', 'DiDi'),
]
PERFIL_CONDUCTOR_SELECTION = [
    ('fragile', 'Frágil'),
    ('standard', 'Estándar'),
    ('solid', 'Sólido'),
]
ESTADO_CARGA_SELECTION = [
    ('not_started', 'Sin iniciar'),
    ('loading', 'Cargando'),
    ('partial', 'Parcial'),
    ('completed', 'Completa'),
    ('load_error', 'Error de carga'),
]
VALIDACION_ESTATUS_SELECTION = [
    ('pending', 'Pendiente'),
    ('under_validation', 'En validación'),
    ('validated', 'Validado'),
    ('rejected', 'Rechazado'),
    ('requires_correction', 'Requiere corrección'),
]
ESTATUS_ANALISIS_SELECTION = [
    ('pending', 'Pendiente'),
    ('under_review', 'En revisión'),
    ('approved', 'Aprobado'),
    ('conditional', 'Condicionado'),
    ('rejected', 'Rechazado'),
]
ESTATUS_PAGO_SELECTION = [
    ('down_payment_paid', 'Pago inicial cubierto'),
    ('partial_payment', 'Pago parcial'),
    ('payment_pending', 'Pago pendiente'),
]
ENTREGA_SELECTION = [
    ('scheduled', 'Programada'),
    ('delayed', 'Retrasada'),
    ('delivered', 'Entregada'),
    ('cancelled', 'Cancelada'),
]
ESTATUS_UNIDAD_SELECTION = [
    ('reserved', 'Reservada'),
    ('ready', 'Lista'),
    ('pending_repair', 'Pendiente de reparación'),
]
ESTADO_DEL_CONTRATO_SELECTION = [
    ('draft', 'Borrador'),
    ('pending_signature', 'Pendiente de firma'),
    ('signed', 'Firmado'),
    ('active', 'Activo'),
    ('expired', 'Vencido'),
    ('cancelled', 'Cancelado'),
]

DOCUMENT_ACK_HELP = "Acuse de recepción del documento."


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Los nombres técnicos son los que viajan en el JSON del conector, así que
    # se dejan tal cual los define el contrato de integración: sin el prefijo
    # x_studio_ y sin los sufijos _id / _ids que usaría un campo nacido en
    # código. Renombrarlos rompe el payload.

    show_pilotea_fields = fields.Boolean(
        string='Muestra los campos de Pilotea',
        compute='_compute_show_pilotea_fields',
        help="Técnico: gobierna la visibilidad del bloque de originación.")

    # --- 1. Lead registrado --------------------------------------------------
    curp = fields.Char(string='CURP', size=18)
    plaza = fields.Many2one(comodel_name='fleet.customer.plaza', string='Plaza')
    referido = fields.Char(string='Código de referido')

    # --- 2. Lead asignado ----------------------------------------------------
    hora_asignacion = fields.Datetime(
        string='Hora asignación',
        help="Momento en que el lead se asignó al asesor. Es la base del SLA "
             "de contacto de 2 horas.")

    # --- 3. Prospecto creado -------------------------------------------------
    referencia_originacion = fields.Char(
        string='Referencia de originación', index=True, copy=False,
        help="Identificador del prospecto en el Sistema de Originación, tal "
             "cual lo emite el sistema origen. Es la llave de idempotencia de "
             "la integración: el conector busca por este valor y escribe si lo "
             "encuentra, o crea si no.")

    # --- 4. Prospecto interesado ---------------------------------------------
    app = fields.Selection(selection=APP_SELECTION, string='App')
    interes = fields.Char(string='Interés')

    # --- 5. Perfil preliminar ------------------------------------------------
    ingreso_estimado = fields.Monetary(
        string='Ingreso estimado', currency_field='company_currency')
    capacidad_de_pago = fields.Monetary(
        string='Capacidad de pago', currency_field='company_currency')
    perfil_conductor = fields.Selection(
        selection=PERFIL_CONDUCTOR_SELECTION, string='Perfil conductor')

    # --- 6. Documentación iniciada -------------------------------------------
    estado_carga = fields.Selection(
        selection=ESTADO_CARGA_SELECTION, string='Estado carga')
    estatus_documentacion = fields.Many2many(
        comodel_name='crm.lead.etiqueta.documentacion',
        relation='crm_lead_etiqueta_documentacion_rel',
        column1='lead_id', column2='etiqueta_id',
        string='Estatus documentación')
    identificacion_vigente = fields.Boolean(
        string='Identificación vigente', help=DOCUMENT_ACK_HELP)
    licencia = fields.Boolean(string='Licencia', help=DOCUMENT_ACK_HELP)
    comprobante_de_domicilio = fields.Boolean(
        string='Comprobante de domicilio', help=DOCUMENT_ACK_HELP)
    comprobantes_de_ingresos = fields.Boolean(
        string='Comprobantes de ingresos', help=DOCUMENT_ACK_HELP)
    constancia_fiscal = fields.Boolean(
        string='Constancia fiscal', help=DOCUMENT_ACK_HELP)
    escrito_csf = fields.Boolean(string='Escrito CSF', help=DOCUMENT_ACK_HELP)
    captura_ap_driver = fields.Boolean(
        string='Captura Ap-driver', help=DOCUMENT_ACK_HELP)

    # --- 7. Documentación completa -------------------------------------------
    documentacion_completa = fields.Boolean(
        string='Documentación completa',
        help="Odoo nunca guarda vacío en un booleano: si el conector manda "
             "null se graba falso. Para conservar el valor previo, no enviar "
             "el campo.")
    validacion_estatus = fields.Selection(
        selection=VALIDACION_ESTATUS_SELECTION, string='Validación estatus')

    # --- 8. Análisis crédito -------------------------------------------------
    estatus_analisis = fields.Selection(
        selection=ESTATUS_ANALISIS_SELECTION, string='Estatus análisis')
    score = fields.Float(string='Score')
    reporte_buro = fields.Boolean(string='Reporte buró', help=DOCUMENT_ACK_HELP)
    observaciones = fields.Text(string='Observaciones')

    # --- 9. Aprobado crédito -------------------------------------------------
    producto_sugerido_aprobado = fields.Many2one(
        comodel_name='fleet.customer.producto', string='Producto sugerido')
    pago_semanal = fields.Monetary(
        string='Pago semanal', currency_field='company_currency')
    tabla_de_pagos = fields.Boolean(
        string='Tabla de pagos', help=DOCUMENT_ACK_HELP)

    # --- 10. Oferta presentada -----------------------------------------------
    unidad_sugerida = fields.Many2one(
        comodel_name='fleet.vehicle', string='Unidad sugerida')
    caracteristicas_de_la_unidad = fields.Char(
        string='Características de la unidad')
    condiciones_comerciales = fields.Html(string='Condiciones comerciales')
    oferta_presentada = fields.Many2many(
        comodel_name='crm.lead.etiqueta.oferta',
        relation='crm_lead_etiqueta_oferta_rel',
        column1='lead_id', column2='etiqueta_id',
        string='Oferta presentada')

    # --- 11. Pago inicial confirmado -----------------------------------------
    pago_inicial = fields.Monetary(
        string='Pago inicial', currency_field='company_currency')
    estatus_pago = fields.Selection(
        selection=ESTATUS_PAGO_SELECTION, string='Estatus pago')
    comprobante_pago_anticipado = fields.Boolean(
        string='Comprobante pago anticipado', help=DOCUMENT_ACK_HELP)

    # --- 12. Programación entrega --------------------------------------------
    fecha_de_entrega = fields.Datetime(string='Fecha de entrega programada')
    fecha_de_entrega_efectiva = fields.Datetime(
        string='Fecha de entrega efectiva')
    entrega = fields.Selection(selection=ENTREGA_SELECTION, string='Entrega')
    entregado = fields.Boolean(string='Entregado')
    responsable = fields.Many2one(
        comodel_name='hr.employee', string='Responsable',
        help="Apunta al empleado, no al usuario: la llave de asesor acordada "
             "es el correo de trabajo.")

    # --- 13. Vehículo asignado -----------------------------------------------
    vehiculo = fields.Many2one(comodel_name='fleet.vehicle', string='Vehículo')
    # Campo maestro: el modelo y el VIN cuelgan de él en lugar de capturarse
    # aparte, que es lo que pedía la nota del contrato para los dos campos
    # marcados como Readonly.
    modelo = fields.Many2one(related='vehiculo.model_id', string='Modelo')
    vin = fields.Char(related='vehiculo.vin_sn', string='VIN')
    estatus_de_la_unidad = fields.Many2one(
        comodel_name='fleet.vehicle.state', string='Estatus de la unidad')
    estatus_unidad = fields.Selection(
        selection=ESTATUS_UNIDAD_SELECTION, string='Estatus unidad')

    # --- 14. Contrato firmado ------------------------------------------------
    estado_del_contrato = fields.Selection(
        selection=ESTADO_DEL_CONTRATO_SELECTION, string='Estado del contrato')
    fecha_de_la_firma = fields.Date(string='Fecha de la firma')
    contrato_de_arrendamiento = fields.Boolean(
        string='Contrato de arrendamiento', help=DOCUMENT_ACK_HELP)
    ratificacion_de_condiciones_contratadas = fields.Boolean(
        string='Ratificación de condiciones contratadas', help=DOCUMENT_ACK_HELP)

    # --- 15. Cliente activo --------------------------------------------------
    fecha_inicio_del_contrato = fields.Date(
        string='Fecha inicio del contrato',
        help="El sistema de originación es el dueño del dato. Odoo no lo "
             "recalcula.")
    producto_contratado_aprobado = fields.Many2one(
        comodel_name='fleet.customer.producto', string='Producto contratado')

    _referencia_originacion_uniq = models.Constraint(
        'unique(referencia_originacion)',
        'Ya existe un lead con esa referencia de originación.',
    )

    @api.depends_context('allowed_company_ids')
    def _compute_show_pilotea_fields(self):
        """Show the origination block only while Pilotea is an active company.

        These fields describe one company's funnel, so on the other company's
        CRM they are noise. The rule is the active companies of the session,
        not the lead's own company: an agent working with Pilotea selected
        sees them on every lead, and unselecting it hides the whole block.
        """
        visible = bool(self.env.companies.filtered('es_pilotea'))
        for lead in self:
            lead.show_pilotea_fields = visible
