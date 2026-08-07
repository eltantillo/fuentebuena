from odoo import fields, models, api
from odoo.exceptions import UserError
from lxml import etree
import base64
import logging
_logger = logging.getLogger(__name__)

class XMLParse(models.Model):
    _name = 'xml.parse'
    _description = 'XML Parse'

    @api.model
    def crear_desde_cfdi(self, xml_bytes):
        NS = {
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'tfd':  'http://www.sat.gob.mx/TimbreFiscalDigital',
        }
        NS_33 = {
            'cfdi': 'http://www.sat.gob.mx/cfd/3',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
        }
        try:
            root = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as e:
            raise UserError(f"XML Invalido {e}")
        version = root.get('Version') or root.get('version', '4.0')
        ns = NS if version.startswith('4') else NS_33

        emisor = root.find('cfdi:Emisor', ns)
        concepto = root.find('.//cfdi:Concepto', ns)
        receptor = root.find('cfdi:Receptor', ns)
        timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
        traslado = root.find('.//cfdi:Traslado', ns)
        if timbre is None:
            raise UserError(f"XML no contiene timbre fiscal")
        uuid = timbre.get('UUID')
        vals = {
            'serie': root.get('Serie') if root is not None else '',
            'folio': root.get('Folio') if root is not None else '',
            'uuid': uuid,
            'rfc_emisor': emisor.get('Rfc') if emisor is not None else '',
            'nombre_emisor': emisor.get('Nombre') if emisor is not None else '',
            'rfc_receptor': receptor.get('Rfc') if receptor is not None else '',
            'nombre_receptor': receptor.get('Nombre') if receptor is not None else '',
            'fecha': root.get('Fecha','').replace('T', ' '),
            'subtotal': float(root.get('SubTotal', 0)),
            'total': float(root.get('Total', 0)),
            'moneda': root.get('Moneda', 'MXN'),
            'impuesto': traslado.get('Importe') if traslado is not None else '',
            'uso_cfdi': receptor.get('UsoCFDI') if receptor is not None else '',
            'Descripcion': concepto.get('Descripcion') if emisor is not None else '',
        }
        return vals
