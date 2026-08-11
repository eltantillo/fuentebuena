# -*- coding: utf-8 -*-

import base64
import json
import requests
import random
import datetime
import string
from lxml import etree
import xmltodict
from zeep import Client
from zeep.transports import Transport

from odoo import fields, models, api,_
from odoo.exceptions import UserError
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import mm
from . import amount_to_text_es_MX
from json.decoder import JSONDecodeError
import pytz
from odoo import tools
import ast
import logging
_logger = logging.getLogger(__name__)

class CfdiRetencionLine(models.Model):
    _name = "cfdi.retencion.line"
    
    cfdi_retencion_id= fields.Many2one('cfdi.retencion',string="CFDI Retencion")
    impuesto = fields.Selection(
        selection=[('001', 'ISR'),
                   ('002', 'IVA'),
                   ('003', 'IEPS'),],
        string='Impuesto', 
    )
    tipo_pago = fields.Selection(
        selection=[('01', 'Pago definitivo IVA'),
                   ('02', 'Pago definitivo IEPS'),
                   ('03', 'Pago definitivo ISR '),
                   ('04', 'Pago provisional ISR '),],
        string='Tipo de pago',
    )

    monto_base = fields.Float(string='Monto base', digits='Product Price', required=True, default=1)
    monto_retenido = fields.Float(string='Monto retenido', digits='Product Price', required=True, default=1)
    monto_exento = fields.Float(string='Monto exento', digits='Product Price', required=True, default=1)
    monto_gravado = fields.Float(string='Monto gravado', digits='Product Price', required=True, default=1)

class CfdiPlataformasLine(models.Model):
    _name = "cfdi.plataforma.line"

    cfdi_retencion_id= fields.Many2one('cfdi.retencion',string="CFDI Retencion")
    pt_rfc_tercero = fields.Char(string="RFC tercero")
    pt_formapagoserv = fields.Selection(
        selection=[('01', 'Efectivo'),
                   ('02', 'Transferencia electrónica de fondos'),
                   ('03', 'Tarjeta de crédito'),
                   ('04', 'Monedero electrónico'),
                   ('05', 'Dinero electrónico'),
                   ('06', 'Tarjeta de débito'),
                   ('07', 'Tarjeta de servicios'),
                   ('08', 'Intermediario pagos'),
                   ('09', 'Otros ingresos por premios, bonificaciones o análogos.'),
                   ],
        string="Forma de pago",
    )
    pt_subtiposerv = fields.Selection(
        selection=[('01', 'Personal'),
                   ('02', 'Compartido'),
                   ('03', 'Plus'),
                   ('04', 'Cancelación'),
                   ],
        string="SubTipo servicio",
    )

    pt_fecha = fields.Date(string="Fecha")
    pt_precio_sin_iva = fields.Float(string='Precio sin IVA')
    pt_impuesto_importe = fields.Float(string='Monto Impuesto')
    pt_impuesto_base = fields.Float(string='Base comisión')
    pt_impuesto_tipo = fields.Selection(selection=[('02', 'IVA'),
                                           ('03', ' IEPS'),
                                           ('01', 'ISR')], string='Impuesto')
    pt_impuesto_tf = fields.Selection(selection=[('Tasa', 'Tasa'),
                                           ('Cuota', 'Cuota'),
                                           ('Exento', 'Exento')], string='Tipo factor')
    pt_impuesto_tasacuota = fields.Float(string='Tasa Impuesto %')
    pt_importe = fields.Float(string='Importe comisión')

class CfdiRetencion(models.Model):
    _name = "cfdi.retencion"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "number"

    factura_cfdi = fields.Boolean('Factura CFDI', copy=False)
    number = fields.Char(string="Numero", store=True, readonly=True, copy=False,
                         default=lambda self: _('Factura borrador'))
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('valid', 'Validada'),
        ('cancel', 'Cancelada'),
    ], string='Status', index=True, readonly=True, default='draft', )

    partner_id = fields.Many2one('res.partner', string="Cliente", required=True)
    fecha_factura = fields.Datetime(string='Fecha Factura', copy=False)
    retencion = fields.Selection(
        selection=[('01', 'Servicios profesionales'), 
                   ('02', 'Regalías por derechos de autor'), 
                   ('03', 'Autotransporte terrestre de carga'),
                   ('04', 'Servicios prestados por comisionistas'), 
                   ('05', 'Arrendamiento'),
                   ('06', 'Enajenación de acciones'), 
                   ('07', 'Enajenación de bienes objeto de la LIEPS'), 
                   ('08', 'Enajenación de bienes inmuebles consignada en escritura pública'), 
                   ('09', 'Enajenación de otros bienes, no consignada en escritura pública.'), 
                   ('10', 'Adquisición de desperdicios industriales.'), 
                   ('11', 'Adquisición de bienes consignada en escritura pública.'), 
                   ('12', 'Adquisición de otros bienes, no consignada en escritura pública.'), 
                   ('13', 'Otros retiros de AFORE.'), 
                   ('14', 'Dividendos o utilidades distribuidas.'), 
                   ('15', 'Remanente distribuible.'), 
                   ('16', 'Intereses.'), 
                   ('17', 'Arrendamiento en fideicomiso.'), 
                   ('18', 'Pagos realizados a favor de residentes en el extranjero.'), 
                   ('19', 'Enajenación de acciones u operaciones en bolsa de valores.'), 
                   ('20', 'Obtención de premios.'), 
                   ('21', 'Fideicomisos que no realizan actividades empresariales.'), 
                   ('22', 'Planes personales de retiro.'),
                   ('23', 'Intereses reales deducibles por créditos hipotecarios.'), 
                   ('24', 'Intereses reales deducibles por créditos hipotecarios.'), 
                   ('25', 'Otro tipo de retenciones.'),
                   ('26', 'Servicios mediante Plataformas Tecnológicas '), 
                   ('27', 'Sector Financiero'),
                   ('28', 'Pagos y retenciones a Contribuyentes del RIF'),],
        string='Retención'
    )
    periodo_inicio = fields.Selection(
        selection=[('01', 'Enero'),
                   ('02', 'Febrero'),
                   ('03', 'Marzo'),
                   ('04', 'Abril'),
                   ('05', 'Mayo'),
                   ('06', 'Junio'),
                   ('07', 'Julio'),
                   ('08', 'Agosto'),
                   ('09', 'Septiembre'),
                   ('10', 'Octubre'),
                   ('11', 'Noviembre'),
                   ('12', 'Diciembre'), ],
        string='Mes inicio',
    )
    periodo_final = fields.Selection(
        selection=[('01', 'Enero'),
                   ('02', 'Febrero'),
                   ('03', 'Marzo'),
                   ('04', 'Abril'),
                   ('05', 'Mayo'),
                   ('06', 'Junio'),
                   ('07', 'Julio'),
                   ('08', 'Agosto'),
                   ('09', 'Septiembre'),
                   ('10', 'Octubre'),
                   ('11', 'Noviembre'),
                   ('12', 'Diciembre'), ],
        string='Mes final',
    )
    ejercicio = fields.Selection(
        selection=[('2022', '2022'),
                   ('2023', '2023'),
                   ('2024', '2024'),
                   ('2025', '2025'),
                   ('2026', '2026'), ],
        string='Ejercicio',
    )

    complemento_a = fields.Boolean('Arrendamiento')
    complemento_b = fields.Boolean('Enajenación de acciones')
    complemento_c = fields.Boolean('Dividendos')
    complemento_d = fields.Boolean('Fideicomiso no empresarial')
    complemento_e = fields.Boolean('Intereses hipotecarios')
    complemento_f = fields.Boolean('Operaciones con derivados')
    complemento_g = fields.Boolean('Pagos a extanjeros')
    complemento_h = fields.Boolean('Planes de retiros')
    complemento_i = fields.Boolean('Premios')
    complemento_j = fields.Boolean('Intereses')
    complemento_k = fields.Boolean('Plataformas tecnológicas')
    complemento_l = fields.Boolean('Sector financiero')

    estado_factura = fields.Selection(
        selection=[('factura_no_generada', 'Factura no generada'), ('factura_correcta', 'Factura correcta'),
                   ('solicitud_cancelar', 'Cancelación en proceso'), ('factura_cancelada', 'Factura cancelada'),
                   ('solicitud_rechazada', 'Cancelación rechazada'), ],
        string='Estado de factura',
        default='factura_no_generada',
        readonly=True,
        copy=False
    )

    qr_value = fields.Char(string='QR Code Value')
    qrcode_image = fields.Binary("QRCode")

    invoice_date = fields.Datetime(string="Fecha de factura")
    retencion_line_ids = fields.One2many('cfdi.retencion.line', 'cfdi_retencion_id', string='CFDI Retencion Line', copy=True)
    currency_id = fields.Many2one('res.currency',string='Moneda',default=lambda self: self.env.company.currency_id, required=True)
    amount_operation = fields.Float(string='Monto operación', store=True, readonly=True, compute='_compute_amount',
                                   currency_field='currency_id')
    amount_exento = fields.Float(string='Exento', store=True, readonly=True, compute='_compute_amount',
                                   currency_field='currency_id')
    amount_gravado = fields.Float(string='Gravado', store=True, readonly=True, compute='_compute_amount',
                                   currency_field='currency_id')
    amount_retenido = fields.Float(string='Total retenido', store=True, readonly=True, compute='_compute_amount',
                                   currency_field='currency_id')

    numero_cetificado = fields.Char(string='Numero de cetificado', copy=False)
    cetificaso_sat = fields.Char(string='Cetificao SAT', copy=False)
    folio_fiscal = fields.Char(string='Folio Fiscal', readonly=True, copy=False)
    fecha_certificacion = fields.Char(string='Fecha y Hora Certificación', copy=False)
    cadena_origenal = fields.Char(string='Cadena Origenal del Complemento digital de SAT', copy=False)
    selo_digital_cdfi = fields.Char(string='Selo Digital del CDFI', copy=False)
    selo_sat = fields.Char(string='Selo del SAT', copy=False)
    moneda = fields.Char(string='Moneda')
    tipocambio = fields.Char(string='TipoCambio')
    number_folio = fields.Char(string='Folio', compute='_get_number_folio')
    qr_value = fields.Char(string='QR Code Value', copy=False)
    invoice_datetime = fields.Char(string='11/12/17 12:34:12')
    proceso_timbrado = fields.Boolean(string='Proceso de timbrado')

    company_id = fields.Many2one('res.company', 'Compañia', default=lambda self: self.env.company)

    tipo_relacion = fields.Selection(
        selection=[('01', 'Nota de crédito de los documentos relacionados'),
                   ('02', 'Nota de débito de los documentos relacionados'),
                   ('03', 'Devolución de mercancía sobre facturas o traslados previos'),
                   ('04', 'Sustitución de los CFDI previos'),
                   ('05', 'Traslados de mercancías facturados previamente'),
                   ('06', 'Factura generada por los traslados previos'),
                   ('07', 'CFDI por aplicación de anticipo')],
        string='Tipo relación'
    )

    uuid_relacionado = fields.Char(string='CFDI Relacionado')

    ####### Campos para complemento dividendos    #################
    tipo_diviendo = fields.Selection(
        selection=[('01', 'Proviene de CUFIN'),
                   ('02', 'No proviene de CUFIN'),
                   ('03', 'Reembolso o reducción de capital'),
                   ('04', 'Liquidación de la persona moral'),
                   ('05', 'CUFINRE'),
                   ('06', 'Proviene de CUFIN al 31 de diciembre 2013.'), ],
        string='Tipo dividendo o utilidad distribuida',
    )
    montisracredmx = fields.Float(string='Monto ISR acreditado Mexico')
    montisracredex = fields.Float(string='Monto ISR acreditado Extranjero')
    montretex = fields.Float(string='Monto ISR retenido Extranjero')
    tiposocdistr = fields.Selection(
        selection=[('Sociedad Nacional', 'Sociedad Nacional'),
                   ('Sociedad Extranjera', 'Sociedad Extranjera'), ],
        string='Tipo de sociedad',
    )
    montisracrednal = fields.Float(string='Monto ISR acreditable nacional')
    montdivacumnal = fields.Float(string='Monto dividendo acumulable nacional')
    montdivacumnex = fields.Float(string='Monto dividendo acumulable extranjero')
    div_remanente = fields.Float(string='Remanente')

    ############### Campos complemento pagos a extranjeros ###########################
    benefefectdelcobro = fields.Selection(
        selection=[('SI', 'SI'),
                   ('NO', 'NO'), ],
        string='Beneficiario Efectivo del Cobro', default='SI'
    )
    pais_residencia = fields.Many2one('res.country', string='Pais de residencia del extrajero')
    concepto_pago = fields.Selection(
        selection=[('1', 'Artistas, deportistas y espectáculos públicos'),
                   ('2', 'Otras personas físicas'),
                   ('3', 'Persona moral'),
                   ('4', 'Fideicomiso'),
                   ('5', 'Asociación en participación'),
                   ('6', 'Organizaciones Internacionales o de gobierno'),
                   ('7', 'Organizaciones exentas'),
                   ('8', 'Agentes pagadores'),
                   ('9', 'Otros'),],
        string='Concepto de pago',
    )
    descripcion_concepto = fields.Char(string="Descripcion / Concepto")
    rfc_beneficiario = fields.Char(string="RFC Representante legal")
    curp_beneficiario = fields.Char(string="CURP Representante legal")
    razon_social_beneficiario = fields.Char(string="Razón social del beneficiario")

    ############### Campos complemento plataformas tecnológicas ###########################

    pt_periodicidad = fields.Selection(
        selection=[('01', 'Semanal'),
                   ('02', 'Mensual'),
                   ('03', 'Diario'),
                   ('04', 'Quincenal'),
                   ('05', 'Otro'), 
                   ],
        string="Periodicidad",
    )
    pt_tipodeserv = fields.Selection(
        selection=[('01', 'Transporte terrestre de pasajeros'),
                   ('02', 'Entrega de alimentos preparados'),
                   ('03', 'Entrega de bienes (distintos de alimentos preparados)'),
                   ('04', 'Hospedaje'),
                   ('05', 'Comercio de bienes'),
                   ('06', 'Otro tipo de servicios'),
                   ('07', 'Descarga o acceso a contenido digital, así como otros contenidos multimedia'),
                   ('08', 'Clubes en línea y páginas de citas'),
                   ('09', 'Enseñanza a distancia o test o ejercicios'),],
        string="Tipo de servicio",
    )
    pt_tot_sin_iva = fields.Float(string='Servicios sin IVA', digits = (12,6))
    pt_tot_iva_tras = fields.Float(string='IVA trasladado', digits = (12,6))
    pt_tot_iva_ret = fields.Float(string='IVA retenido', digits = (12,6))
    pt_tot_isr_ret = fields.Float(string='ISR retenido', digits = (12,6))
    pt_tot_uso_plataforma = fields.Float(string='Uso de plataforma', digits = (12,6))

    plataformas_line_ids = fields.One2many('cfdi.plataforma.line', 'cfdi_retencion_id', string='CFDI Plataformas Line', copy=True)

    ###########################################################################

    @api.model
    def _get_cadena_xslts(self):
        return 'l10n_mx_edi/data/4.0/xslt/cadenaoriginal_TFD.xslt', 'l10n_mx_edi_retenciones/data/retenciones.xslt'

    @api.model
    def _decode_cfdi_attachment(self, cfdi_data):
        """ Extract relevant data from the CFDI attachment.

        :param: cfdi_data:      The cfdi data as raw bytes.
        :return:                A python dictionary.
        """
        cadena_tfd, cadena = self._get_cadena_xslts()

        def get_cadena(cfdi_node, template):
            if cfdi_node is None:
                return None
            cadena_root = etree.parse(tools.file_open(template))
            return str(etree.XSLT(cadena_root)(cfdi_node))

        def get_node(node, xpath):
            nodes = node.xpath(xpath)
            return nodes[0] if nodes else None

        def get_value(node, key):
            if node is None:
                return None
            upper_key = key[0].upper() + key[1:]
            lower_key = key[0].lower() + key[1:]
            return node.get(upper_key) or node.get(lower_key)

        # Nothing to decode.
        if not cfdi_data:
            return {}

        try:
            cfdi_node = etree.fromstring(cfdi_data)
            emisor_node = get_node(cfdi_node, "//*[local-name()='Emisor']")
            receptor_node = get_node(cfdi_node, "//*[local-name()='Receptor']")
            info_global_node = get_node(cfdi_node, "//*[local-name()='InformacionGlobal']")
            origin_node = get_node(cfdi_node, "//*[local-name()='CfdiRelacionados']")
            origin_nodes = cfdi_node.xpath("//*[local-name()='CfdiRelacionado']")
        except etree.XMLSyntaxError:
            # Not an xml
            return {}
        except AttributeError:
            # Not a CFDI
            return {}

        tfd_node = get_node(cfdi_node, "//*[local-name()='TimbreFiscalDigital']")
        origin_type = get_value(origin_node, 'TipoRelacion')
        origin_uuids = [origin_uuid for node in origin_nodes if (origin_uuid := get_value(node, 'UUID'))]
        if origin_type and origin_uuids:
            origin_uuids_str = ','.join(origin_uuids)
            origin = f'{origin_type}|{origin_uuids_str}'
        else:
            origin = None

        return {
            'uuid': get_value(tfd_node, 'UUID'),
            'supplier_rfc': get_value(emisor_node, 'Rfc'),
            'customer_rfc': get_value(receptor_node, 'Rfc'),
            'amount_total': get_value(cfdi_node, 'Total'),
            'cfdi_node': cfdi_node,
            'usage': get_value(receptor_node, 'UsoCFDI'),
            'payment_method': get_value(cfdi_node, 'formaDePago') or get_value(cfdi_node, 'MetodoPago'),
            'bank_account': get_value(cfdi_node, 'NumCtaPago'),
            'sello': get_value(cfdi_node, 'sello') or 'No identificado',
            'sello_sat': get_value(tfd_node, 'SelloSAT') or 'No identificado',
            'cadena': get_cadena(tfd_node, cadena_tfd) or get_cadena(cfdi_node, cadena),
            'certificate_number': get_value(cfdi_node, 'NoCertificado'),
            'certificate_sat_number': get_value(tfd_node, 'NoCertificadoSAT'),
            'expedition': get_value(cfdi_node, 'LugarExpedicion'),
            'fiscal_regime': get_value(emisor_node, 'RegimenFiscal') or '',
            'emission_date_str': (get_value(cfdi_node, 'Fecha') or '').replace('T', ' '),
            'stamp_date': (get_value(tfd_node, 'FechaTimbrado') or '').replace('T', ' '),
   #         'periodicity': get_value(info_global_node, 'Periodicidad'),
            'origin': origin,
        }


    @api.model
    def _get_retenciones_template(self):
        return 'l10n_mx_edi_retenciones.retencion20'

    def action_cfdi_generate(self):
        """ Try to generate and send the CFDI for the current invoice. """
        self.ensure_one()

        qweb_template = self.env['cfdi.retencion']._get_retenciones_template()

        # == CFDI values ==
        cfdi_values = self.to_json()

        # == Generate the CFDI ==
        certificate = cfdi_values['certificate']
        #self._clean_cfdi_values(cfdi_values)
        #_logger.info('cfdi_values %s', cfdi_values)
        cfdi = self.env['ir.qweb']._render(qweb_template, cfdi_values)
        #_logger.info('cfdi %s', cfdi)
        cfdi_infos = self._decode_cfdi_attachment(cfdi)
        cfdi_cadena_crypted = certificate._sign(cfdi_infos['cadena'], formatting='base64')
#        _logger.info('cfdi2 %s', cfdi_infos)
        cfdi_infos['cfdi_node'].attrib['Sello'] = cfdi_cadena_crypted
#        _logger.info('cfdi2 %s', cfdi_infos)
        cfdi_str = etree.tostring(cfdi_infos['cfdi_node'], pretty_print=True, xml_declaration=True, encoding='UTF-8')
#        _logger.info('cfdi3 %s', cfdi_str)

        # == Check credentials ==
        root_company = self.company_id.sudo().parent_ids[::-1].filtered('l10n_mx_edi_certificate_ids')[:1]
        pac_name = root_company.l10n_mx_edi_pac
        if pac_name == 'sw':
            credentials = self._get_sw_credentials(root_company)
        elif pac_name == 'finkok':
            credentials = self._get_finkok_credentials(root_company)
        else:
            raise UserError(_("No está configurado el PAC Solucion Factible"))

        if credentials.get('errors'):
            raise UserError(_("Error: %s") % (credentials['errors']))

        # == Check PAC ==
        if pac_name == 'sw':
            sign_results = self._sw_sign(credentials, cfdi_str)
        elif pac_name == 'finkok':
            sign_results = self._finkok_sign(credentials, cfdi_str)

        if sign_results.get('errors'):
            raise UserError(_("Error 2: %s") % (sign_results['errors']))

        # == Success ==
        #_logger.info('sign_results %s', sign_results)
        #on_success(cfdi_values, cfdi_filename, sign_results['cfdi_str'], populate_return=populate_return)

        # Receive and store XML invoice
        if sign_results['cfdi_str']:
                self._set_data_from_xml(sign_results['cfdi_str'])
#                self._set_data_from_xml(base64.b64decode(sign_results['cfdi_str']))
                file_name = self.number.replace('/', '_') + '.xml'
                self.env['ir.attachment'].sudo().create(
                    {
                        'name': file_name,
                        'datas': base64.b64encode(sign_results['cfdi_str']),
                        # 'datas_fname': file_name,
                        'res_model': self._name,
                        'res_id': self.id,
                        'type': 'binary'
                    })

        self.write({'estado_factura': 'factura_correcta',
                           'factura_cfdi': True,})
        self.message_post(body="CFDI emitido")

    @api.depends('number')
    def _get_number_folio(self):
        if self.number:
            self.number_folio = self.number.replace('RET','').replace('/', '')

    @api.model
    def _get_amount_2_text(self, amount_total):
        return amount_to_text_es_MX.get_amount_to_text(self, amount_total, 'es_cheque', self.currency_id.name)

    @api.model
    def _default_journal(self):
        if not self.journal_id:
            company_id = self._context.get('default_company_id', self.env.company.id)
            return self.env['account.journal'].search([('type','=','sale'),('company_id', '=', company_id)],limit=1)

    journal_id = fields.Many2one('account.journal', 'Diario', default=_default_journal)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number', _('Draft Invoice')) == _('Draft Invoice'):
                if 'company_id' in vals:
                    vals['number'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('cfdi.retencion') or _('Draft Invoice')
                else:
                    vals['number'] = self.env['ir.sequence'].next_by_code('cfdi.retencion') or _('Draft Invoice')
        result = super(CfdiRetencion, self).create(vals_list)
        return result

    def action_valid(self):
        self.write({'state': 'valid'})
        if not self.invoice_date:
            self.invoice_date = datetime.datetime.now()
        
    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.depends('retencion_line_ids')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_operation = sum(round_curr(line.monto_exento) for line in self.retencion_line_ids) + sum(line.monto_gravado for line in self.retencion_line_ids)
        self.amount_exento = sum(round_curr(line.monto_exento) for line in self.retencion_line_ids)
        self.amount_gravado = sum(line.monto_gravado for line in self.retencion_line_ids)
        self.amount_retenido = sum(round_curr(line.monto_retenido) for line in self.retencion_line_ids)

    @api.model
    def to_json(self):

        root_company = self.company_id.sudo().parent_ids[::-1].filtered('l10n_mx_edi_certificate_ids')[:1]
        if root_company.l10n_mx_edi_pac:
            pac_test_env = root_company.l10n_mx_edi_pac_test_env
            pac_password = root_company.sudo().l10n_mx_edi_pac_password
            if not pac_test_env and not pac_password:
                raise UserError(_("Falta aregar credenciales al PAC"))
        else:
            raise UserError(_("Falta especificar el PAC"))

        certificate_sudo = root_company.sudo().l10n_mx_edi_certificate_ids.filtered('is_valid')[:1]
        if not certificate_sudo:
            raise UserError(_("No se encontró un certificado válido"))
        if not root_company.vat:
            raise UserError(_("Falta configurar el RFC en la compañía."))

        nombre = self.partner_id.name.upper()
        zipreceptor = self.partner_id.zip

        #corregir hora
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.env.user.partner_id.tz or 'America/Mexico_City'
        # timezone = tools.ustr(timezone).encode('utf-8')

        local = pytz.timezone(timezone)
        if not self.fecha_factura:
           naive_from = datetime.datetime.now()
        else:
           naive_from = self.fecha_factura
        local_dt_from = naive_from.replace(tzinfo=pytz.UTC).astimezone(local)
        date_from = local_dt_from.strftime ("%Y-%m-%dT%H:%M:%S")
        if not self.fecha_factura:
           self.fecha_factura = datetime.datetime.now()

        request_params = {
                'certificate': certificate_sudo,
                'factura': {
                      'FolioInt': self.number.replace('RET','').replace('/',''),
                      'FechaExp': date_from,
                      'CveRetenc': self.retencion,
                      'LugarExpRetenc': self.company_id.partner_id.commercial_partner_id.zip,
                      'DescRetenc': '0',
                      'serie': 'R',
                      'folio': self.number.replace('RET','').replace('/',''),

                      'no_certificado': ('%x' % int(certificate_sudo.serial_number))[1::2],
                      'certificado': certificate_sudo._get_der_certificate_bytes(formatting='base64').decode(),
                },
                'emisor': {
                      'RfcE': root_company.vat.upper(),
                      'NomDenRazSocE': root_company.name.upper(),
                      'NacionalidadR': 'Nacional',
                      'RegimenFiscalE': root_company.l10n_mx_edi_fiscal_regime,
                },
                'receptor': {
                      'NacionalidadR': 'Nacional' if self.partner_id.vat.upper() != 'XEXX010101000' else 'Extranjero',
                      'NomDenRazSocR': nombre,
                      'RfcR': self.partner_id.vat.upper() if self.partner_id.vat.upper() != 'XEXX010101000' else '',
                      'CurpR': None, #revisar este!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                      'DomicilioFiscalR': self.partner_id.zip,
                      'NumRegIdTribR': self.partner_id.vat if self.partner_id.vat.upper() == 'XEXX010101000' else '',
                },
                'periodo': {
                      'MesIni': self.periodo_inicio,
                      'MesFin': self.periodo_final,
                      'Ejercicio': self.ejercicio,
                },
                'totales': {
                      'MontoTotOperacion': round(self.amount_gravado,2) + round(self.amount_exento,2),
                      'MontoTotGrav': round(self.amount_gravado,2) if self.amount_gravado>0 else '0.00',
                      'MontoTotExent': round(self.amount_exento,2) if self.amount_exento>0 else '0.00',
                      'MontoTotRet': round(self.amount_retenido,2) if self.amount_retenido>0 else '0.00',
                  #    'UtilidadBimestral': self.periodo_final, #opcional
                  #    'ISRCorrespondiente': self.ejercicio,  #opcional
                },
        }

        #items = {'numerodepartidas': len(self.retencion_line_ids)}
        retencion_lines = []
        for line in self.retencion_line_ids:
                retencion_lines.append({'BaseRet': round(line.monto_base,2),
                                      'ImpuestoRet': line.impuesto,
                                      'MontoRet': round(line.monto_retenido,2),
                                      'TipoPagoRet': line.tipo_pago,})

        request_params.update({'ImpRetenidos': retencion_lines})

        if self.uuid_relacionado:
            cfdi_relacionado = []
            uuids = self.uuid_relacionado.replace(' ', '').split(',')
            for uuid in uuids:
                cfdi_relacionado.append({
                    'uuid': uuid,
                })
            request_params.update({'CfdisRelacionados': {'UUID': cfdi_relacionado, 'TipoRelacion': self.tipo_relacion}})

        #######     Agrega complemento dividendos    #################
        if self.complemento_c:
            request_params.update({
                    'DividOUtil': {
                         'CveTipDivOUtil': self.tipo_diviendo,
                         'MontISRAcredRetMexico': self.montisracredmx,
                         'MontISRAcredRetExtranjero': self.montisracredex or '0',
                         'MontRetExtDivExt': self.montretex,
                         'TipoSocDistrDiv': self.tiposocdistr,
                         'MontISRAcredNal': self.montisracrednal,
                         'MontDivAcumNal': self.montdivacumnal,
                         'MontDivAcumExt': self.montdivacumnex or '0',
                    },
                    'Remanente': {
                         'ProporcionRem': self.div_remanente
                    }
            })
        #######     Agrega complemento pagos a extranjeros    #################
        if self.complemento_g:
            if self.benefefectdelcobro == 'NO':
               request_params.update({
                    'Pagosaextranjeros': {
                         'EsBenefEfectDelCobro': self.benefefectdelcobro,
                         'PaisDeResidParaEfecFisc': self.pais_residencia.code,
                         'ConceptoPago': self.concepto_pago,
                         'DescripcionConcepto': self.descripcion_concepto,
                    },
               })
            elif self.benefefectdelcobro == 'SI':
               request_params.update({
                    'Pagosaextranjeros': {
                         'EsBenefEfectDelCobro': self.benefefectdelcobro,
                         'ConceptoPago': self.concepto_pago,
                         'DescripcionConcepto': self.descripcion_concepto,
                         'RFC': self.rfc_beneficiario,
                         'CURP': self.curp_beneficiario,
                         'NomDenRazSocB': self.razon_social_beneficiario,
                    },
               })
        #######     Agrega complemento plataformas    #################
        if self.complemento_k:

            monto_efectivo = 0
            for line in self.plataformas_line_ids:
                if line.pt_formapagoserv == '01':
                    monto_efectivo += line.pt_impuesto_importe
            request_params.update({
                    'plataformasTecnologicas': {
                         'Periodicidad': self.pt_periodicidad,
                         'NumServ': len(self.plataformas_line_ids),
                         'MonTotServSIVA': round(self.pt_tot_sin_iva,6),
                         'TotalIVATrasladado': round(self.pt_tot_iva_tras,6),
                         'TotalIVARetenido': round(self.pt_tot_iva_ret,6),
                         'TotalISRRetenido': round(self.pt_tot_isr_ret,6),
                         'DifIVAEntregadoPrestServ':  round(self.pt_tot_iva_tras - self.pt_tot_iva_ret - monto_efectivo, 6) if self.partner_id.vat.upper() != 'XEXX010101000' else '0.0',
                         'MonTotalporUsoPlataforma': round(self.pt_tot_uso_plataforma,6),
                    },
            })
            plataforma_lines = []
            for line in self.plataformas_line_ids:
                plataforma_lines.append({'FechaServ': str(line.pt_fecha),
                                         'TipoDeServ': self.pt_tipodeserv,
                                         'SubTipServ': line.pt_subtiposerv,
                                         'RFCTerceroAutorizado': line.pt_rfc_tercero,
                                         'FormaPagoServ': line.pt_formapagoserv,
                                         'PrecioServSinIVA': line.pt_precio_sin_iva,
                                         'Base': round(line.pt_impuesto_base,2),
                                         'Impuesto': line.pt_impuesto_tipo,
                                         'TipoFactor': line.pt_impuesto_tf,
                                         'TasaCuota': self.set_decimals(line.pt_impuesto_tasacuota/100, 6),
                                         'Importe': round(line.pt_impuesto_base * line.pt_impuesto_tasacuota/100, 6),
                                         'ComisionDelServicio': line.pt_importe,
                                         })
            if plataforma_lines:
                request_params.update({'servicios': plataforma_lines})

        return request_params

    def clean_text(self, text):
        clean_text = text.replace('\n', ' ').replace('\\', ' ').replace('-', ' ').replace('/', ' ').replace('|', ' ')
        clean_text = clean_text.replace(',', ' ').replace(';', ' ').replace('>', ' ').replace('<', ' ')
        return clean_text[:1000]

    def set_decimals(self, amount, precision):
        if amount is None or amount is False:
            return None
        return '%.*f' % (precision, amount)

    def _set_data_from_xml(self, xml_invoice):
        if not xml_invoice:
            return None
        NSMAP = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'retenciones': 'http://www.sat.gob.mx/esquemas/retencionpago/2',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
        }

        xml_data = etree.fromstring(xml_invoice)
        Complemento = xml_data.find('retenciones:Complemento', NSMAP)
        TimbreFiscalDigital = Complemento.find('tfd:TimbreFiscalDigital', NSMAP)

        #self.tipocambio = xml_data.attrib['TipoCambio']
    #    self.moneda = xml_data.attrib['Moneda']
        self.numero_cetificado = xml_data.attrib['NoCertificado']
        self.cetificaso_sat = TimbreFiscalDigital.attrib['NoCertificadoSAT']
        self.fecha_certificacion = TimbreFiscalDigital.attrib['FechaTimbrado']
        self.selo_digital_cdfi = TimbreFiscalDigital.attrib['SelloCFD']
        self.selo_sat = TimbreFiscalDigital.attrib['SelloSAT']
        self.folio_fiscal = TimbreFiscalDigital.attrib['UUID']
        self.invoice_datetime = xml_data.attrib['FechaExp']
        version = TimbreFiscalDigital.attrib['Version']
        self.cadena_origenal = '||%s|%s|%s|%s|%s||' % (version, self.folio_fiscal, self.fecha_certificacion,
                                                       self.selo_digital_cdfi, self.cetificaso_sat)

        options = {'width': 275 * mm, 'height': 275 * mm}
        amount_str = str(self.amount_operation).split('.')
        qr_value = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?&id=%s&re=%s&rr=%s&tt=%s.%s&fe=%s' % (
            self.folio_fiscal,
            self.company_id.vat,
            self.partner_id.vat,
            amount_str[0].zfill(10),
            amount_str[1].ljust(6, '0'),
            self.selo_digital_cdfi[-8:],
        )
        self.qr_value = qr_value
        ret_val = createBarcodeDrawing('QR', value=qr_value, **options)
        self.qrcode_image = base64.encodebytes(ret_val.asString('jpg'))


    def action_cfdi_cancel(self):
        for invoice in self:
            if invoice.factura_cfdi:
                if invoice.estado_factura == 'factura_cancelada':
                    pass
                    # raise UserError(_('La factura ya fue cancelada, no puede volver a cancelarse.'))

                root_company = self.company_id.sudo().parent_ids[::-1].filtered('l10n_mx_edi_certificate_ids')[:1]
                pac_name = root_company.l10n_mx_edi_pac
                if pac_name == 'sw':
                    credentials = self._get_sw_credentials(root_company)
                elif pac_name == 'finkok':
                    credentials = self._get_finkok_credentials(root_company)
                else:
                    raise UserError(_("No está configurado el PAC Solucion Factible"))

                if credentials.get('errors'):
                    raise UserError(_("Error: %s") % (credentials['errors']))

                if pac_name == 'sw':
                    json_response = self._sw_cancel(root_company, credentials, invoice.folio_fiscal, self.env.context.get('motivo_cancelacion','02'), cancel_uuid=self.env.context.get('foliosustitucion',''))
                elif pac_name == 'finkok':
                    json_response = self._finkok_cancel(root_company, credentials, invoice.folio_fiscal, self.env.context.get('motivo_cancelacion','02'), cancel_uuid=self.env.context.get('foliosustitucion',''))

                #_logger.info('json response %s', json_response)
                log_msg = ''
                if pac_name == 'sw':
                    if json_response['status'] != 'success':
                        raise UserError(_("Error en la cancelación"))
                elif pac_name == 'finkok':
                    if json_response['errors']:
                        raise UserError(_("Error en la cancelación %s") % (json_response.get('errors', {})))
                
                #if pac_name == 'sw':
                file_name = 'CANCEL_' + invoice.number.replace('/', '_') + '.xml'
                self.env['ir.attachment'].sudo().create(
                        {
                            'name': file_name,
                            'datas': base64.b64encode(json_response.get('data', {}).get('acuse', {}).encode("utf-8")),
                            # 'datas_fname': file_name,
                            'res_model': self._name,
                            'res_id': invoice.id,
                            'type': 'binary'
                        })
                log_msg = "CFDI Cancelado"
                invoice.write({'estado_factura': 'factura_cancelada'})

    def send_factura_mail(self):
        self.ensure_one()
        template = self.env.ref('l10n_mx_edi_retenciones.email_template_factura_retencion', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
            
        ctx = dict()
        ctx.update({
            'default_model': 'cfdi.retencion',
            'default_res_ids': self.ids,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def unlink(self):
        raise UserError("Los registros no se pueden borrar, solo cancelar.")

    # -------------------------------------------------------------------------
    # CFDI: PACs
    # -------------------------------------------------------------------------
    @api.model
    def _document_get_sw_token(self, credentials):
        if credentials['password'] and not credentials['username']:
            # token is configured directly instead of user/password
            return {
                'token': credentials['password'].strip(),
            }

        try:
            headers = {
                'user': credentials['username'],
                'password': credentials['password'],
                'Cache-Control': "no-cache"
            }
            response = requests.post(credentials['login_url'], headers=headers, timeout=20)
            response.raise_for_status()
            response_json = response.json()
            return {
                'token': response_json['data']['token'],
            }
        except (requests.exceptions.RequestException, KeyError, TypeError) as req_e:
            return {
                'errors': [str(req_e)],
            }

    @api.model
    def _get_sw_credentials(self, company):
        if not company.sudo().l10n_mx_edi_pac_password:
            return {
                'errors': [_("The username and/or password are missing.")]
            }

        credentials = {
            'username': company.sudo().l10n_mx_edi_pac_username,
            'password': company.sudo().l10n_mx_edi_pac_password,
        }

        if company.l10n_mx_edi_pac_test_env:
            credentials.update({
                'login_url': 'https://services.test.sw.com.mx/security/authenticate',
                'sign_url': 'https://services.test.sw.com.mx/retencion/stamp/v3',
                'cancel_url': 'https://services.test.sw.com.mx/cfdi33/cancel/csd',
            })
        else:
            credentials.update({
                'login_url': 'https://services.sw.com.mx/security/authenticate',
                'sign_url': 'https://services.sw.com.mx/retencion/stamp/v3',
                'cancel_url': 'https://services.sw.com.mx/cfdi33/cancel/csd',
            })

        # Retrieve a valid token.
        credentials.update(self._document_get_sw_token(credentials))

        return credentials

    @api.model
    def _document_sw_call(self, url, headers, payload=None):
        try:
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                verify=True,
                timeout=20,
            )
#            _logger.info('call 01 %s', response.text)
            #_logger.info('content 01 %s', response.content.decode('UTF-8'))
        except requests.exceptions.RequestException as req_e:
#            _logger.info('call 02')
            return {'status': 'error', 'message': str(req_e)}
        msg = ""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as res_e:
#            _logger.info('call 04')
            msg = str(res_e)
        try:
            response_json = response.json()
        except JSONDecodeError:
            # If it is not possible get json then
            # use response exception message
            return {'status': 'error', 'message': msg}
        if (response_json['status'] == 'error' and
                response_json['message'].startswith('307')):
            # XML signed previously
            cfdi = base64.encodebytes(
                response_json['messageDetail'].encode('UTF-8'))
            cfdi = cfdi.decode('UTF-8')
            response_json['data'] = {'cfdi': cfdi}
            # We do not need an error message if XML signed was
            # retrieved then cleaning them
            response_json.update({
                'message': None,
                'messageDetail': None,
                'status': 'success',
            })
        return response_json

    @api.model
    def _sw_sign(self, credentials, cfdi):
        ''' calls the SW web service to send and sign the CFDI XML.
        Method does not depend on a recordset
        '''
        #cfdi_b64 = base64.encodebytes(cfdi).decode('UTF-8')
        cfdi_b64 = cfdi.decode('UTF-8')
        random_values = [random.choice(string.ascii_letters + string.digits) for n in range(30)]
        boundary = ''.join(random_values)
        payload = """--%(boundary)s
Content-Type: text/xml
Content-Transfer-Encoding: binary
Content-Disposition: form-data; name="xml"; filename="xml"

%(cfdi_b64)s
--%(boundary)s--
""" % {'boundary': boundary, 'cfdi_b64': cfdi_b64}
        payload = payload.replace('\n', '\r\n').encode('UTF-8')
#        _logger.info('payload1 %s', payload)

        headers = {
            'Authorization': "bearer " + credentials['token'],
            'Content-Type': ('multipart/form-data; '
                             'boundary="%s"') % boundary,
        }
#        _logger.info('headers %s', headers)
        response_json = self._document_sw_call(credentials['sign_url'], headers, payload=payload)

#        _logger.info('response_json33 %s', response_json)

        try:
            cfdi_signed = response_json['data']['retencion']
        except (KeyError, TypeError):
            cfdi_signed = None

        if cfdi_signed:
            return {
                'cfdi_str': cfdi_signed.encode('UTF-8'),
            }
        else:
            code = response_json.get('message')
            msg = response_json.get('messageDetail')
            errors = []
            if code:
                errors.append(_("Code : %s", code))
            if msg:
                errors.append(_("Message : %s", msg))
            return {'errors': errors}

    @api.model
    def _document_sw_cancel_call(self, url, headers, payload=None):
        try:
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                verify=True,
                timeout=20,
            )
        except requests.exceptions.RequestException as req_e:
            return {'status': 'error', 'message': str(req_e)}
        msg = ""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as res_e:
            msg = str(res_e)
        try:
            response_json = response.json()
        except JSONDecodeError:
            return {'status': 'error', 'message': msg}
        if (response_json['status'] == 'error' and response_json['message'].startswith('307')):
            # XML signed previously
            cfdi = base64.encodebytes(
                response_json['messageDetail'].encode('UTF-8'))
            cfdi = cfdi.decode('UTF-8')
            response_json['data'] = {'cfdi': cfdi}
            # We do not need an error message if XML signed was
            # retrieved then cleaning them
            response_json.update({
                'message': None,
                'messageDetail': None,
                'status': 'success',
            })
        return response_json

    @api.model
    def _sw_cancel(self, company, credentials, uuid, cancel_reason, cancel_uuid=None):
        headers = {
            'Authorization': "bearer " + credentials['token'],
            'Content-Type': "application/json"
        }
        certificates = company.l10n_mx_edi_certificate_ids
        certificate = certificates.sudo()._get_valid_certificate()
        payload_dict = {
            'rfc': company.vat,
            'b64Cer': certificate.content.decode('UTF-8'),
            'b64Key': certificate.key.decode('UTF-8'),
            'password': certificate.password,
            'uuid': uuid,
            'motivo': cancel_reason,
        }
        if cancel_uuid:
            payload_dict['folioSustitucion'] = cancel_uuid
        payload = json.dumps(payload_dict)

        response_json = self._document_sw_cancel_call(credentials['cancel_url'], headers, payload=payload.encode('UTF-8'))
        cancelled = response_json['status'] == 'success'
        if cancelled:
            data_codes = response_json.get('data', {}).get('uuid', {}).values()
            data_code = next(iter(data_codes)) if data_codes else ''
            code = '' if data_code in ('201', '202') else data_code
            msg = '' if data_code in ('201', '202') else _("Cancelling got an error")
        else:
            code = response_json.get('message')
            msg = response_json.get('messageDetail')
            raise UserError(_("Error: %s -- %s") % response_json.get('message'), response_json.get('messageDetail'))
        return response_json

    @api.model
    def _get_finkok_credentials(self, company):
        ''' Return the company credentials for PAC: finkok. Does not depend on a recordset
        '''
        if company.l10n_mx_edi_pac_test_env:
            return {
                'username': 'cfdi@vauxoo.com',
                'password': 'vAux00__',
                'sign_url': 'https://demo-facturacion.finkok.com/servicios/soap/retentions.wsdl',
                'cancel_url': 'http://demo-facturacion.finkok.com/servicios/soap/cancel.wsdl',
            }
        else:
            if not company.sudo().l10n_mx_edi_pac_username or not company.sudo().l10n_mx_edi_pac_password:
                return {
                    'errors': [_("The username and/or password are missing.")]
                }

            return {
                'username': company.sudo().l10n_mx_edi_pac_username,
                'password': company.sudo().l10n_mx_edi_pac_password,
                'sign_url': 'https://facturacion.finkok.com/servicios/soap/retentions.wsdl',
                'cancel_url': 'http://facturacion.finkok.com/servicios/soap/cancel.wsdl',
            }

    @api.model
    def _finkok_sign(self, credentials, cfdi):
        ''' Send the CFDI XML document to Finkok for signature. Does not depend on a recordset
        '''
        try:
            transport = Transport(timeout=20)
            client = Client(credentials['sign_url'], transport=transport)
            response = client.service.stamp(cfdi, credentials['username'], credentials['password'])
            # pylint: disable=broad-except
        except Exception as e:
            return {
                'errors': [_("The Finkok service failed to sign with the following error: %s", str(e))],
            }

        if response.Incidencias and not response.xml:
            if 'CodigoError' in response.Incidencias.Incidencia[0]:
                code = response.Incidencias.Incidencia[0].CodigoError
            else:
                code = None
            if 'MensajeIncidencia' in response.Incidencias.Incidencia[0]:
                msg = response.Incidencias.Incidencia[0].MensajeIncidencia
            else:
                msg = None
            errors = []
            if code:
                errors.append(_("Code : %s", code))
            if msg:
                errors.append(_("Message : %s", msg))
            return {'errors': errors}

        cfdi_signed = response.xml if 'xml' in response else None
        if cfdi_signed:
            cfdi_signed = cfdi_signed.encode('utf-8')

        return {
            'cfdi_str': cfdi_signed,
        }

    @api.model
    def _finkok_cancel(self, company, credentials, uuid, cancel_reason, cancel_uuid=None):
        certificates = company.l10n_mx_edi_certificate_ids
        certificate = certificates.sudo()._get_valid_certificate()
        cer_pem = certificate._get_pem_cer(certificate.content)
        key_pem = certificate._get_pem_key(certificate.key, certificate.password)
        try:
            transport = Transport(timeout=20)
            client = Client(credentials['cancel_url'], transport=transport)
            factory = client.type_factory('apps.services.soap.core.views')
            uuid_type = factory.UUID()
            uuid_type.UUID = uuid
            uuid_type.Motivo = cancel_reason
            if cancel_uuid:
                uuid_type.FolioSustitucion = cancel_uuid
            docs_list = factory.UUIDArray(uuid_type)
            response = client.service.cancel(
                docs_list,
                credentials['username'],
                credentials['password'],
                company.vat,
                cer_pem,
                key_pem,
            )
            # pylint: disable=broad-except
        except Exception as e:
            return {
                'errors': [_("The Finkok service failed to cancel with the following error: %s", str(e))],
            }

        code = None
        msg = None
        if 'Folios' in response and response.Folios:
            if 'EstatusUUID' in response.Folios.Folio[0]:
                response_code = response.Folios.Folio[0].EstatusUUID
                if response_code not in ('201', '202'):
                    code = response_code
                    msg = _("Cancelling got an error")
        elif 'CodEstatus' in response:
            code = response.CodEstatus
            msg = _("Cancelling got an error")
        else:
            msg = _('A delay of 2 hours has to be respected before to cancel')

        errors = []
        if code:
            errors.append(_("Code : %s", code))
        if msg:
            errors.append(_("Message : %s", msg))
        if errors:
            return {'errors': errors}

        return {}

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _compute_attachment_ids(self):
        res = super(MailComposeMessage, self)._compute_attachment_ids()
        for rec in self:
            if self.model == 'cfdi.retencion':
                attachment_ids=[]
                template_id = self.env.ref('l10n_mx_edi_retenciones.email_template_factura_retencion')
                if self.template_id.id == template_id.id:
                    res_ids = ast.literal_eval(self.res_ids)
                    for res_id in res_ids:
                        retencion = self.env[self.model].browse(res_id)
                        domain = [
                            ('res_id', '=', retencion.id),
                            ('res_model', '=', retencion._name),
                            ('name', '=', retencion.number.replace('/', '_') + '.xml')]
                        xml_file = self.env['ir.attachment'].search(domain, limit=1)
                        if xml_file:
                            attachment_ids.extend(rec.attachment_ids.ids)
                            attachment_ids.append(xml_file.id)
                    if attachment_ids:
                        rec.attachment_ids = [(6, 0, attachment_ids)]
        return res

