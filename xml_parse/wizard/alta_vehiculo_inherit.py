from odoo import fields,models,api
import base64
import logging
import re
import datetime

_logger = logging.getLogger(__name__)

class AltaVehiculoInherit(models.TransientModel):

    _inherit = "alta.vehiculo"

    folio_uuid = fields.Char(
        string='UUID',
    )
    factura = fields.Char(
        string='Factura',
    )
    rfc_emisor = fields.Char(
        string='RFC Emisor'
    )
    nom_emisor = fields.Char(
        string='Nombre emisor'
    )
    rfc_receptor = fields.Char(
        string='RFC Receptor'
    )
    nom_receptor = fields.Char(
        string='Nombre receptor'
    )
    fecha = fields.Datetime(
        string='Fecha',
    )
    total = fields.Float(
        string='Total',
    )
    moneda =fields.Char(
        string='Moneda'
    )
    uso_cfdi = fields.Char(
        string='Uso CFDI'
    )
    document_xml = fields.Binary(
        string="Documento",
    )
    nombre_archivo = fields.Char(
        string="Nombre archivo",
    )
    model_id = fields.Many2one(
        comodel_name='fleet.vehicle.model',
        string='Modelo',
    )
    version_id = fields.Many2one(
        comodel_name='fleet.customer.version',
        string='Versión',
    )
    year = fields.Char(
        string='Año',
    )
    color = fields.Char(
        string='Color',
    )
    vin_sn = fields.Char(
        string="VIN SN",
    )
    importe_adquisicion = fields.Float(
        string="Importe de adquisición",
    )
    iva_adquisicion = fields.Float(
        string="Iva de adquisición",
    )
    pdf_factura = fields.Binary(
        string="PDF de factura"
    )
    num_puertas = fields.Integer(
        string="Número de puertas",
    )


    def buscar_entidad(self, entidades, descripcion):
        descripcion = (descripcion or '').upper()
        for entidad in entidades:
            nombre = (entidad.name or '').upper()
            patron = rf'\b{re.escape(nombre)}\b'
            if re.search(patron, descripcion):
                return entidad
        return False

    def buscar_year(self, descripcion):
        year_now = datetime.datetime.now().year
        descripcion = (descripcion or '').upper()
        valid_years = [str(year) for year in range(2018, year_now + 1)]
        for year in reversed(valid_years):
            patron = rf'\b{year}\b'
            if re.search(patron, descripcion):
                return year
        return False

    def buscar_transmision(self, descripcion):
        transmisiones = {
            'AUTOMATICA': 'automatic',
            'AUTOMATICA': 'automatic',
            'AUTOMATICA': 'automatic',
            'CVT': 'automatic',
            'MANUAL': 'manual',
            'STD': 'manual',
            'STANDAR': 'manual',
        }
        texto = " ".join(descripcion.split())
        for trans, valor in transmisiones.items():
            patron = rf'\b{trans}\b'
            if re.search(patron, texto, re.IGNORECASE):
                return valor
        return False

    def buscar_vin_sn(self, descripcion):
        patrones = [
            r'NO\.\s*SERIE:\s*([A-HJ-NPR-Z0-9]{17})',
            r'N[º°]\s*CHASIS:\s*([A-HJ-NPR-Z0-9]{17})',
            r'\b([A-HJ-NPR-Z0-9]{17})\b',
        ]
        for patron in patrones:
            match = re.search(patron, descripcion or '', re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return False

    def extraer_color(self, descripcion):
        patrones = [
            r'COLOR\s+EXTERIOR:\s*([^,]+)',
            r'COLOR:\s*(.*?)\s+TRANSMISION:',
        ]
        for patron in patrones:
            match = re.search(patron, descripcion, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return False

    def extraer_num_puertas(self, descripcion):
        puertas = 0
        patrones = [
            r'NO.\s+PUERTAS:\s*([0-9]+)',
            r'NUMERO\s+PUERTAS:\s*([0-9]+)',
        ]
        for patron in patrones:
            match = re.search(patron, descripcion, re.IGNORECASE)
            if match:
                puertas =  match.group(1).strip()

    def extraer_num_motor(self, descripcion):
        patrones = [
            r'(MOTOR\s+HECHO\s+EN\s+[A-Za-zÁÉÍÓÚáéíóú]+)',
            r'NO\.?\s*MOTOR:\s*([A-Z0-9]+)',
        ]

        for patron in patrones:
            match = re.search(patron, descripcion or '', re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return False

    @api.onchange('document_xml')
    def _onchange_document_xml(self):
        modelos = self.env['fleet.vehicle.model'].search([])
        versiones = self.env['fleet.customer.version'].search([])
        modelos_ordenados = sorted(modelos,key=lambda m: len(m.name or ''),reverse=True)
        modelos_ids = {
            m.name: m.id for m in modelos
        }
        self.folio_uuid = False
        self.model_id = False
        self.version_id = False
        self.year = False
        self.color = False
        self.transmission = False
        self.vin_sn = False
        self.num_motor = False
        self.factura = False
        self.fecha = False
        self.total = 0
        self.importe_adquisicion = 0
        self.iva_adquisicion = 0
        self.num_puertas = 0
        if not self.document_xml:
            return
        try:
            xml_bytes = base64.b64decode(self.document_xml)
        except Exception:
            return
        data = self.env['xml.parse'].crear_desde_cfdi(xml_bytes)
        descripcion = (data.get('Descripcion') or '').upper()
        modelo_encontrado = self.buscar_entidad(
            modelos_ordenados,
            descripcion
        )
        if modelo_encontrado:
            modelo_id = modelos_ids.get(modelo_encontrado.name)
            self.model_id = modelo_id
            versiones_filtradas = versiones.filtered( lambda v: v.model_id.id == modelo_id)
            map_versiones = {v.name: v.id  for v in versiones_filtradas}
            versiones_ordenadas = sorted(versiones_filtradas,key=lambda v: len(v.name or ''),reverse=True)
            version_encontrada = self.buscar_entidad(versiones_ordenadas,descripcion)
            if version_encontrada:
                self.version_id = map_versiones.get(version_encontrada.name)
        year_v = self.buscar_year(descripcion)
        if year_v:
            self.year = year_v
        color = self.extraer_color(descripcion)
        if color:
            self.color = color
        transmision = self.buscar_transmision(descripcion)
        if transmision:
            self.transmission = transmision
        vin_sn = self.buscar_vin_sn(descripcion)
        if vin_sn:
            self.vin_sn = vin_sn
        num_motor = self.extraer_num_motor(descripcion)
        if num_motor:
            self.num_motor = num_motor
        puertas = self.extraer_num_puertas(descripcion)
        puertas = int(puertas) if puertas else 0
        if puertas == 0:
            if version_encontrada:
                etapa_rentado = self.env['fleet.vehicle.state'].search([('es_etapa_rentado', '=', True)])
                vehiculo = self.env['fleet.vehicle'].search(
                    [('state_id', '=', etapa_rentado.id),
                     ('model_id', '=', modelo_id),
                     ('model_year','=', year_v),
                     ('version','=', map_versiones.get(version_encontrada.name))], limit=1
                )
                _logger.info(f"Vehiculo: {vehiculo}")
                puertas = vehiculo.doors
        self.num_puertas = puertas
        self.factura = f"{data['serie']} {data['folio']}"
        self.fecha = data['fecha']
        self.folio_uuid = data['uuid']
        self.importe_adquisicion = data['subtotal']
        self.iva_adquisicion = data['impuesto']
        self.total = (
                self.importe_adquisicion +
                self.iva_adquisicion
        )

    def alta(self):
        for record in self:
            record.env['fleet.vehicle'].create({
                'state_id': record.estado_id.id,
                'model_id': record.model_id.id,
                'version': record.version_id.id,
                'model_year': record.year,
                'color': record.color,
                'es_gnv': record.es_gnv,
                'transmission': record.transmission,
                'vin_sn': record.vin_sn,
                'numero_motor': record.num_motor,
                'flotilla_id': record.flotilla_id.id,
                'producto_id': record.producto_id.id,
                'plaza_id': record.plaza_id.id,
                'doors': record.num_puertas,
                'orden_compra_id': self.env.context.get('active_id'),
                #Datos fiscales
                'fecha_adquisicion': record.fecha,
                'factura': record.factura,
                'fecha_factura': record.fecha,
                'folio_uuid': record.folio_uuid,
                #Importes
                'importe_adquisicion': record.importe_adquisicion,
                'iva_adquisicion': record.iva_adquisicion,
                'importe_total_adquisicion': record.total,
                #documentos
                'factura_vehiculo': record.pdf_factura,
                'xml_factura': record.document_xml,
                #Proveedor
                'proveedor_id': self.env.context.get('default_proveedor_id'),
            })