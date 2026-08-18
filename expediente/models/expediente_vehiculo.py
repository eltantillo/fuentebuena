import base64
import io
import zipfile

from odoo import api, fields, models

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

import logging
_logger = logging.getLogger(__name__)


class ExpedienteVehiculo(models.Model):
    _inherit = 'fleet.vehicle'


    def check_expediente_completo(self, expediente_tipo_id):
        self.ensure_one()
        faltantes = []
        expediente_tipo = self.env['expediente.tipo'].browse(expediente_tipo_id)
        if expediente_tipo.factura_req and not self.existe_factura:
            faltantes.append('Factura')
        if expediente_tipo.opcion_compra_req and not self.existe_opcion_compra:
            faltantes.append('Opción a Compra')
        if expediente_tipo.poliza_req:
            poliza = self.get_poliza()
            if not poliza or not poliza.existe_attach_poliza:
                faltantes.append('Póliza')
        if expediente_tipo.endoso_req:
            endoso = self.get_endoso()
            if not endoso or not endoso.existe_attach_poliza:
                faltantes.append('Endoso')
        if expediente_tipo.contrato_req:
            contrato = self.get_contrato_record()
            if not contrato or not contrato.existe_attach_contrato:
                faltantes.append('Contrato')
        if expediente_tipo.tipo_tramite_ids:
            tramites_con_archivo = self.tramite_ids.filtered('existe_expediente').mapped('tipo_tramite_id')
            for tramite_req in expediente_tipo.tipo_tramite_ids:
                if tramite_req not in tramites_con_archivo:
                    faltantes.append(f'Trámite: {tramite_req.name}')
        if expediente_tipo.tipo_adecuacion_ids:
            adecuaciones_con_archivo = self.adecuacion_ids.filtered('existe_expediente_arch').mapped('adecuacion_id')
            for adecuacion_req in expediente_tipo.tipo_adecuacion_ids:
                if adecuacion_req.name == 'GNV' and not self.es_gnv:
                    continue
                if adecuacion_req not in adecuaciones_con_archivo:
                    faltantes.append(f'Adecuación: {adecuacion_req.name}')
        return {
            'completo': len(faltantes) == 0,
            'faltantes': faltantes
        }

    @api.model
    def return_validacion_expe(self, vehiculos, tipo_expe):
        vehiculos_recs = self.browse(vehiculos).exists()
        return [
            {
                'vehiculo': vehiculo.vin_sn,
                'plaza': vehiculo.plaza_id.name,
                'expediente': 'completo' if validacion['completo'] else 'incompleto',
                'faltantes': validacion['faltantes'],
            }
            for vehiculo in vehiculos_recs
            for validacion in [vehiculo.check_expediente_completo(tipo_expe)]
        ]

    @api.model
    def get_expediente_type(self, expediente_tipo_id, vehiculo_id):
        vehiculo = self.browse(vehiculo_id)
        expediente_tipo = self.env['expediente.tipo'].browse(expediente_tipo_id)
        faltantes = []
        factura_data = None
        if expediente_tipo.factura_req:
            if vehiculo.existe_factura:
                factura_data = vehiculo.get_factura(type='with_data')
            else:
                faltantes.append('Factura')
        opcion_compra_data = None
        if expediente_tipo.opcion_compra_req:
            if vehiculo.existe_opcion_compra:
                opcion_compra_data = vehiculo.get_opcion_compra(type='with_data')
            else:
                faltantes.append('Opción a compra')
        polizas_list = []
        if expediente_tipo.poliza_req:
            poliza = vehiculo.get_poliza()
            if poliza and poliza.existe_attach_poliza:
                poliza_doc = vehiculo._helper_build_doc_dict(
                    poliza, 'attach_poliza', poliza.tipo_poliza_id.name or 'poliza', type='with_data'
                )
                if poliza_doc:
                    polizas_list.append(poliza_doc)
            else:
                faltantes.append('Póliza')
        if expediente_tipo.endoso_req:
            endoso = vehiculo.get_endoso()
            if endoso and endoso.existe_attach_poliza:
                endoso_doc = vehiculo._helper_build_doc_dict(
                    endoso, 'attach_poliza', endoso.tipo_poliza_id.name or 'endoso', type='with_data'
                )
                if endoso_doc:
                    polizas_list.append(endoso_doc)
            else:
                faltantes.append('Endoso')
        contrato_data = None
        if expediente_tipo.contrato_req:
            contrato_data = vehiculo.get_contrato(type='with_data')
            if not contrato_data:
                faltantes.append('Contrato')
        tramites_list = []
        if expediente_tipo.tipo_tramite_ids:
            tramites_con_archivo = vehiculo.tramite_ids.filtered('existe_expediente')
            tramites_tipos_existentes = tramites_con_archivo.mapped('tipo_tramite_id')
            for tramite_req in expediente_tipo.tipo_tramite_ids:
                if tramite_req in tramites_tipos_existentes:
                    rec = tramites_con_archivo.filtered(lambda t: t.tipo_tramite_id == tramite_req)[:1]
                    name = tramite_req.name.replace(' ', '_')
                    doc = vehiculo._helper_build_doc_dict(rec, 'expediente', name, type='with_data')
                    if doc:
                        tramites_list.append(doc)
                else:
                    faltantes.append(f'Trámite: {tramite_req.name}')
        adecuaciones_list = []
        if expediente_tipo.tipo_adecuacion_ids:
            adecuaciones_con_archivo = vehiculo.adecuacion_ids.filtered('existe_expediente_arch')
            adecuaciones_tipos_existentes = adecuaciones_con_archivo.mapped('adecuacion_id')
            for adecuacion_req in expediente_tipo.tipo_adecuacion_ids:
                if adecuacion_req.name == 'GNV' and not vehiculo.es_gnv:
                    continue
                if adecuacion_req in adecuaciones_tipos_existentes:
                    rec = adecuaciones_con_archivo.filtered(lambda a: a.adecuacion_id == adecuacion_req)[:1]
                    name = adecuacion_req.name.replace(' ', '_')
                    doc = vehiculo._helper_build_doc_dict(rec, 'expediente_arch', name, type='with_data')
                    if doc:
                        adecuaciones_list.append(doc)
                else:
                    faltantes.append(f'Adecuación: {adecuacion_req.name}')
        return {
            'factura': factura_data,
            'opcion_compra': opcion_compra_data,
            'adecuaciones': adecuaciones_list or None,
            'tramites': tramites_list or None,
            'contrato': contrato_data,
            'polizas': polizas_list or None,
            'faltantes': faltantes
        }

    @api.model
    def get_expediente(self, vehiculo_id, type="without_data"):
        vehiculo = self.browse(vehiculo_id)
        return {
            'factura': vehiculo.get_factura(type='with_data'),
            'opcion_compra': vehiculo.get_opcion_compra(type='with_data'),
            'adecuaciones': vehiculo.get_adecuaciones(type='with_data') or None,
            'tramites': vehiculo.get_tramites(type='with_data') or None,
            'contrato': vehiculo.get_contrato(type='with_data'),
            'polizas': vehiculo.get_polizas(type='with_data') or None,
        }

    def _helper_build_doc_dict(self, record, binary_field_name, default_name, type="without_data"):
        if not record:
            return None
        vin = self.vin_sn or 'SIN_VIN'
        vals = {
            'id': record.id,
            'name': f"{default_name}_{vin}.pdf"
        }
        if type == 'with_data':
            binary_data = getattr(record, binary_field_name, False)
            if not binary_data:
                return None
            vals.update({
                'data': binary_data,
                'mimetype': 'application/pdf',
                'size': len(binary_data),
            })
        return vals

    def get_factura(self, type="without_data"):
        self.ensure_one()
        if not self.existe_factura:
            return None
        return self._helper_build_doc_dict(self, 'factura_vehiculo', 'factura', type=type)

    def get_opcion_compra(self, type="without_data"):
        self.ensure_one()
        if not self.existe_opcion_compra:
            return None
        return self._helper_build_doc_dict(self, 'opcion_compra', 'opcion_compra', type=type)

    def _get_poliza_por_tipo(self, nombre_tipo):
        self.ensure_one()
        tipo = self.env['fleet.poliza.tipo'].search([('name', '=', nombre_tipo)], limit=1)
        if not tipo:
            return self.env['fleet.poliza']
        return self.poliza_ids.filtered(lambda p: p.tipo_poliza_id == tipo).sorted(key=lambda p: p.id)[-1:]

    def get_poliza(self):
        return self._get_poliza_por_tipo("Póliza")

    def get_endoso(self):
        return self._get_poliza_por_tipo("Endoso")

    def get_polizas(self, type="without_data"):
        self.ensure_one()
        dicc = []
        for record in self.poliza_ids.filtered('existe_attach_poliza'):
            doc_type_name = record.tipo_poliza_id.name if record.tipo_poliza_id else 'poliza'
            doc = self._helper_build_doc_dict(record, 'attach_poliza', doc_type_name, type=type)
            if doc:
                dicc.append(doc)
        return dicc or None

    def get_adecuaciones(self, type="without_data"):
        self.ensure_one()
        dicc = []
        for record in self.adecuacion_ids.filtered('existe_expediente_arch'):
            name = record.adecuacion_id.name.replace(' ', '_') if record.adecuacion_id else 'adecuacion'
            doc = self._helper_build_doc_dict(record, 'expediente_arch', name, type=type)
            if doc:
                dicc.append(doc)
        return dicc or None

    def get_tramites(self, type="without_data"):
        self.ensure_one()
        dicc = []
        for record in self.tramite_ids.filtered('existe_expediente'):
            name = record.tipo_tramite_id.name.replace(' ', '_') if record.tipo_tramite_id else 'tramite'
            doc = self._helper_build_doc_dict(record, 'expediente', name, type=type)
            if doc:
                dicc.append(doc)
        return dicc or None

    def get_contrato_record(self):
        self.ensure_one()
        return self.env['fleet.vehicle.log.contract'].search(
            [('vehicle_id', '=', self.id)],
            limit=1,
            order='id desc'
        )

    def get_contrato(self, type="without_data"):
        self.ensure_one()
        contrato = self.get_contrato_record()
        if contrato and contrato.existe_attach_contrato:
            return self._helper_build_doc_dict(contrato, 'attach_contrato', 'contrato', type=type)
        return None

    @api.model
    def get_zip_expediente(self, vehiculo_id, tipo_expediente = None ):
        vehiculo = self.browse(vehiculo_id)
        if not vehiculo.exists():
            return None
        if tipo_expediente:
            expediente = vehiculo.get_expediente_type(tipo_expediente,vehiculo.id)
        else:
            expediente = vehiculo.get_expediente(vehiculo.id)
        documentos = []
        for clave in ('factura', 'opcion_compra', 'contrato'):
            doc = expediente.get(clave)
            if doc:
                documentos.append(doc)
        for clave in ('polizas', 'tramites', 'adecuaciones'):
            documentos.extend(expediente.get(clave) or [])
        if not documentos:
            return None
        buffer = io.BytesIO()
        nombres_usados = {}
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archivo_zip:
            for doc in documentos:
                if not doc.get('data'):
                    continue
                nombre = doc['name']
                nombres_usados[nombre] = nombres_usados.get(nombre, 0) + 1
                if nombres_usados[nombre] > 1:
                    base, _, ext = nombre.rpartition('.')
                    nombre = f"{base or nombre}_{nombres_usados[nombre]}.{ext or 'pdf'}"
                contenido = base64.b64decode(doc['data'])
                archivo_zip.writestr(nombre, contenido)
        buffer.seek(0)
        vin = vehiculo.vin_sn or 'SIN_VIN'
        return {
            'name': f'expediente_{vin}.zip',
            'data': base64.b64encode(buffer.read()).decode('utf-8'),
            'mimetype': 'application/zip',
        }

    @api.model
    def get_faltantes_excel(self, vehiculos, tipo_expe, estado=False):
        if xlsxwriter is None:
            raise ImportError(
                "El módulo 'xlsxwriter' no está instalado en el servidor. "
                "Instálalo con: pip install xlsxwriter"
            )
        resultados = self.return_validacion_expe(vehiculos, tipo_expe)
        if estado:
            resultados = [r for r in resultados if r['expediente'] == estado]
        expediente_tipo = self.env['expediente.tipo'].browse(tipo_expe)
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        sheet = workbook.add_worksheet('Expedientes')
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#283A3E',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        ok_format = workbook.add_format({'font_color': '#00B377', 'bold': True})
        bad_format = workbook.add_format({'font_color': '#FF2D55', 'bold': True})
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        sheet.write(0, 0, 'VIN', header_format)
        sheet.write(0,1, 'Plaza', header_format)
        sheet.write(0, 2, 'Estado', header_format)
        sheet.write(0, 3, 'Faltantes', header_format)
        sheet.set_column(0, 0, 22)
        sheet.set_column(1, 1, 14)
        sheet.set_column(2, 2, 14)
        sheet.set_column(3, 3, 60)
        sheet.freeze_panes(1, 0)
        for fila, resultado in enumerate(resultados, start=1):
            sheet.write(fila, 0, resultado['vehiculo'] or 'SIN VIN')
            es_completo = resultado['expediente'] == 'completo'
            sheet.write(fila, 1, resultado['plaza'] or 'SIN PLAZA')
            sheet.write(fila, 2, resultado['expediente'].capitalize(), ok_format if es_completo else bad_format)
            sheet.write(fila, 3, ', '.join(resultado['faltantes']) or '—', wrap_format)
        workbook.close()
        buffer.seek(0)
        nombre_tipo = (expediente_tipo.name or 'expediente').replace(' ', '_')
        sufijo = f'_{estado}' if estado else ''
        return {
            'name': f'faltantes_{nombre_tipo}{sufijo}.xlsx',
            'data': base64.b64encode(buffer.read()).decode('utf-8'),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }

    @api.model
    def _cron_notificar_expedientes(self):
        tipos = self.env['expediente.tipo'].search([('notificar_por_correo', '=', True)])
        vehiculos = self.search([('flotilla_id', '=', 1)])
        for tipo in tipos:
            emails = list(set(
                email
                for email in tipo.usuarios_notificar_ids.mapped('work_email')
                if email
            ))
            if not emails:
                continue
            excel = self.get_faltantes_excel(
                vehiculos.ids,
                tipo.id,
                'incompleto'
            )
            if not excel:
                continue
            attachment = self.env['ir.attachment'].sudo().create({
                'name': excel['name'],
                'type': 'binary',
                'datas': excel['data'],
                'mimetype': excel['mimetype'],
            })
            mail = False
            try:
                mail = self.env['mail.mail'].sudo().create({
                    'subject': f'Estado de expedientes - {tipo.name}',
                    'body_html': f"""
                        <p>Buen día,</p>

                        <p>
                            Se adjunta el reporte correspondiente al tipo de
                            expediente <b>{tipo.name}</b>.
                        </p>

                        <p>
                            El archivo contiene el estado de los expedientes
                            y los documentos faltantes.
                        </p>

                        <p>Saludos.</p>
                    """,
                    'email_to': ','.join(emails),
                    'attachment_ids': [(4, attachment.id)],
                })
                mail.send()
            except Exception as e:
                _logger.info(f"Error al enviar correo: {e}")
            finally:
                if attachment:
                    attachment.unlink()