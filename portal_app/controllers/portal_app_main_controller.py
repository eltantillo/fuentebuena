from odoo import http
from odoo.http import request, content_disposition
from odoo import fields
import logging
import base64

_logger = logging.getLogger(__name__)

class PortalAppMainController(http.Controller):
    @http.route(['/portal'], type='http', auth='public', website=True, sitemap=False)
    def renderizar(self, **kw):
        response = request.render('portal_app.portal_template', {})
        return response

    @http.route(['/portal/log'], type='json', auth='public', website=True, sitemap=False)
    def log_descarga_poliza(self, vehiculo_id):
        existe = request.env['portal.track.poliza'].sudo().search([('vehiculo_id','=', vehiculo_id)], limit=1)
        vals = {
            "etapa": "descargado",
            "fecha_hora_descarga": fields.Datetime.now(),
            "fecha_hora_ult_desc": fields.Datetime.now(),
            "num_descargas": existe.num_descargas + 1,
        }
        if existe:
            if existe.etapa == "pendiente":
                existe.sudo().write(vals)
            elif existe.etapa == "descargado":
                vals.pop("etapa",None)
                vals.pop("fecha_hora_descarga", None)
                existe.sudo().write(vals)
        else:
            vals["vehiculo_id"]=vehiculo_id
            request.env['portal.track.poliza'].sudo().create(vals)


    @http.route(['/portal/user-data'], type='json', auth='public', website=True, sitemap=False)
    def buscar_usuario(self, valor):
        valor = valor.upper().replace(" ", "")
        cliente = request.env['res.partner'].sudo().search(['|',
            ('vat', '=', valor),
            ('curp','=', valor)], limit=1
        )
        if not cliente:
            return None
        return {
            "id": cliente.id
        }

    @http.route(['/portal/vehiculo-data'], type='json', auth='public', website=True, sitemap=False)
    def buscar_vehiculo(self, matricula=None, user=None):
        domain = []
        if matricula:
            matricula = matricula.upper().replace(" ", "")
            domain.append(('license_plate', '=', matricula))
        if user:
            domain.append(('driver_id', '=', int(user)))
        if not domain:
            return None
        vehiculo = request.env['fleet.vehicle'].sudo().search(domain, limit=1)
        if not vehiculo:
            return None
        return {
            "id": vehiculo.id
        }

    @http.route(['/portal/contrato-data'], type='json', auth='public', website=True, sitemap=False)
    def buscar_contrato(self, valor):
        valor = valor.replace(" ", "")
        _logger.info(f'Buscar contrato, valor: {valor}')
        contrato = request.env['fleet.vehicle.log.contract'].sudo().search([('state','=', 'open'),'|',
            ('cie','=', valor),
            ('ins_ref','=', valor)], limit=1, order='id desc'
        )
        if not contrato:
            return None
        return {
            "id": contrato.id,
            "vehicle_id": contrato.vehicle_id.id
        }

    @http.route(['/portal/poliza/<int:poliza_id>'], type='http', auth='public')
    def descargar_poliza(self, poliza_id):
        poliza = request.env['fleet.poliza'].sudo().browse(poliza_id)
        nombre = f"{poliza.vin_sn}_{poliza.tipo_poliza_id.name}_{poliza.num_poliza.replace(" ", "")}.pdf"
        return request.make_response(
            base64.b64decode(poliza.attach_poliza),
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', content_disposition(nombre)),
            ]
        )

    @http.route(['/portal/poliza-data'], type='json', auth='public', website=True, sitemap=False)
    def buscar_poliza(self, vehiculo):
        resultado = {
            "poliza": None,
            "endosos": []
        }
        tipo_endoso = request.env['fleet.poliza.tipo'].sudo().search([('name','=', 'Endoso')])
        tipo_poliza = request.env['fleet.poliza.tipo'].sudo().search([('name','=', 'Póliza')], limit=1)
        poliza = request.env['fleet.poliza'].sudo().search([
            ('vehiculo_id','=', vehiculo),
            ('tipo_poliza_id','=', tipo_poliza.id)],
        limit=1, order='id desc')
        if poliza:
            resultado["poliza"] = {
                "id": poliza.id,
                "url": f"/portal/poliza/{poliza.id}",
                "nombre": f"{poliza.vin_sn}_{poliza.tipo_poliza_id.name}_{poliza.num_poliza.replace(" ", "")}.pdf",
                "tipo": poliza.tipo_poliza_id.name,
            }
        endosos = request.env['fleet.poliza'].sudo().search([
            ('vehiculo_id','=', vehiculo),
            ('tipo_poliza_id','=', tipo_endoso.id),
            ('fecha_inicio', '>', poliza.fecha_inicio)
        ], order='id desc')
        for endoso in endosos:
            resultado["endosos"].append({
                "id": endoso.id,
                "url": f"/portal/poliza/{endoso.id}",
                "nombre": f"{endoso.vin_sn}_{endoso.tipo_poliza_id.name}_{endoso.num_poliza.replace(" ", "")}.pdf",
                "tipo": poliza.endoso.name,
            })
        return resultado


