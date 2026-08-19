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

    dias_expe_incompleto = fields.Integer(
        string='Dias de incompleto',
    )
    def validar_factura(self):
        if not self.existe_factura:
            return {
                'faltante': 'Factura',
                'motivo': 'No existe pdf en el registro'
            }
        else:
            return None

    def validar_opcion_compra(self):
        if not  self.existe_opcion_compra:
            return {
                'faltante': 'Opción a compra',
                'motivo': 'No existe pdf en el registro'
            }
        else:
            return  None

    def validar_contrato(self, contrato):
        if not contrato.existe_attach_contrato:
            return {
                'faltante': 'Contrato',
                'motivo': 'No existe pdf en el registro'
            }
        else:
            if not contrato.state == 'open':
                return {
                    'faltante': 'Contrato',
                    'motivo': 'Requiere contrato abierto'
                }
            else:
                if contrato.expiration_date >= fields.Date.today():
                    return {
                        'faltante': 'Contrato',
                        'motivo': 'Contrato vencido'
                    }
                else:
                    return None

    def validar_tramite(self, tramite, tramite_req):
        if not tramite.existe_expediente:
            return {
                'faltante': f'Trámite: {tramite_req.name}',
                'motivo': 'No existe pdf en el registro'
            }
        else:
            if tramite.tipo_tramite_id.notificar_renovacion == True:
                if not tramite.fecha_vencimiento_renovacion:
                    return {
                        'faltante': f'Trámite: {tramite_req.name}',
                        'motivo': 'No contiene fecha de vencimiento'
                    }
                else:
                    if tramite.fecha_vencimiento_renovacion >= fields.Date.today():
                        return {
                            'faltante': f'Trámite: {tramite_req.name}',
                            'motivo': 'Trámite vencido'
                        }
                    else: return  None
            else: return None

    def validar_adecuacion(self, adecuacion, adecuacion_req):
        if adecuacion_req.name == 'GNV' and self.es_gnv:
            if not adecuacion.existe_expediente_arch:
                return {
                    'faltante': f'Adecuación: {adecuacion_req.name}',
                    'motivo': 'No existe pdf en el registro'
                }
            else: return None
        else: return None

    def validar_poliza(self ,poliza):
        if not poliza.existe_attach_poliza:
            return {
                'faltante': 'Póliza',
                'motivo': 'No existe pdf en el registro'
            }
        else:
            if not poliza.fecha_vencimiento:
                return {
                    'faltante': 'Póliza',
                    'motivo': 'No contiene fecha de vencimiento'
                }
            if poliza.fecha_vencimiento >= fields.Date.today():
                return {
                    'faltante': 'Póliza',
                    'motivo': 'Póliza vencida'
                }
            else:
                return None

    def return_inexistencia(self, faltante):
        return {
            'faltante': faltante,
            'motivo': 'No existe registro'
        }

    def check_expediente_completo(self, expediente_tipo_id):
        self.ensure_one()
        faltantes = []
        completos = []
        expediente_tipo = self.env['expediente.tipo'].browse(expediente_tipo_id)
        if expediente_tipo.factura_req:
            factura = self.validar_factura()
            faltantes.append(factura) if factura else completos.append('factura')
        if expediente_tipo.opcion_compra_req:
            opcion_compra = self.validar_opcion_compra()
            faltantes.append(opcion_compra) if opcion_compra else completos.append('opcion_compra')
        if expediente_tipo.poliza_req:
            poliza = self.poliza_ids.filtered(lambda p: p.tipo_poliza_id.name == 'Póliza').sorted(key=lambda x: x.id, reverse=True)[:1]
            if poliza:
                poliza_v = self.validar_poliza(poliza)
                faltantes.append(poliza_v) if poliza_v else completos.append(f'poliza')
            else:
                faltantes.append(self.return_inexistencia('Póliza'))
        if expediente_tipo.endoso_req:
            endoso = self.poliza_ids.filtered(lambda p: p.tipo_poliza_id.name == 'Endoso').sorted(key=lambda x: x.id, reverse=True)[:1]
            if not endoso:
                faltantes.append(self.return_inexistencia('Endoso'))
            else:
                if endoso.existe_attach_poliza:
                    completos.append('endoso')
                else:
                    faltantes.append({
                        'faltante': 'Endoso',
                        'motivo': 'No existe pdf en el registro'
                    })
        if expediente_tipo.contrato_req:
            contrato = self.get_contrato_record()
            if contrato and self.state_id.name == 'Rentado':
                contrato_v = self.validar_contrato(contrato)
                faltantes.append(contrato_v) if contrato_v else completos.append('contrato')
        if expediente_tipo.tipo_tramite_ids:
            for tramite_req in expediente_tipo.tipo_tramite_ids:
                tramite = self.tramite_ids.filtered(lambda x: x.tipo_tramite_id.id == tramite_req.id).sorted(key=lambda x: x.id, reverse=True)[:1]
                if tramite:
                    tramite_v = self.validar_tramite(tramite, tramite_req)
                    faltantes.append(tramite_v) if tramite_v else completos.append(f'tramite: {tramite_req.name}')
                else:
                    if not (tramite_req.name == 'Dictamen anual GNV' and self.es_gnv):
                        faltantes.append(self.return_inexistencia( f'Trámite: {tramite_req.name}'))
        if expediente_tipo.tipo_adecuacion_ids:
            for adecuacion_req in expediente_tipo.tipo_adecuacion_ids:
                adecuacion = self.adecuacion_ids.filtered(lambda x: x.adecuacion_id.id == adecuacion_req.id).sorted(key=lambda x: x.id, reverse=True)[:1]
                if adecuacion:
                    adecuacion_v = self.validar_adecuacion(adecuacion, adecuacion_req)
                    faltantes.append(adecuacion_v) if adecuacion_v else completos.append(f'adecuacion: {adecuacion_req.name}')
                else:
                    faltantes.append(self.return_inexistencia( f'Adecuación: {adecuacion_req.name}'))
        return {
            'completo': len(faltantes) == 0,
            'faltantes': faltantes,
            'completos': completos
        }

    @api.model
    def return_validacion_expe(self, vehiculos, tipo_expe):
        vehiculos_recs = self.browse(vehiculos).exists()
        return [
            {
                'vehiculo': vehiculo.vin_sn,
                'dias_incompleto': vehiculo.dias_expe_incompleto,
                'plaza': vehiculo.plaza_id.name,
                'etapa': vehiculo.state_id.name,
                'sub_etapa': vehiculo.sub_etapa_id.name,
                'expediente': 'completo' if validacion['completo'] else 'incompleto',
                'faltantes': validacion['faltantes'],
                'completos': validacion['completos']
            }
            for vehiculo in vehiculos_recs
            for validacion in [vehiculo.check_expediente_completo(tipo_expe)]
        ]

    @api.model
    def get_expediente_type(self, expediente_tipo_id, vehiculo_id):
        vehiculo = self.browse(vehiculo_id)
        if not vehiculo.exists():
            return None
        expediente_tipo = self.env['expediente.tipo'].browse(expediente_tipo_id)
        validacion = vehiculo.check_expediente_completo(expediente_tipo_id)
        faltantes = validacion['faltantes']
        completos = validacion['completos']
        factura_data = None
        opcion_compra_data = None
        contrato_data = None
        polizas_list = []
        tramites_list = []
        adecuaciones_list = []
        for archivo in completos:
            if archivo == 'factura':
                factura_data = vehiculo.get_factura(type='with_data')
            if archivo == 'opcion_compra':
                opcion_compra_data = vehiculo.get_opcion_compra(type='with_data')
            if archivo == 'poliza':
                poliza = vehiculo.get_poliza()
                if poliza:
                    poliza_doc = vehiculo._helper_build_doc_dict(
                        poliza,
                        'attach_poliza',
                        poliza.tipo_poliza_id.name or 'poliza',
                        type='with_data'
                    )
                    polizas_list.append(poliza_doc)
            if archivo == 'endoso':
                endoso = vehiculo.get_endoso()
                endoso_doc = vehiculo._helper_build_doc_dict(
                    endoso,
                    'attach_poliza',
                    endoso.tipo_poliza_id.name or 'endoso',
                    type='with_data'
                )
                if endoso:
                    polizas_list.append(endoso_doc)
            if archivo == 'contrato':
                contrato_data = vehiculo.get_contrato(type='with_data')
            if archivo.startswith('tramite'):
                tipo_tramite = archivo.split(":", 1)[1].strip()
                _logger.info("Informacion en tipo tramite")
                _logger.info(tipo_tramite)
                tramite = vehiculo.tramite_ids.filtered(lambda x: x.tipo_tramite_id.name == tipo_tramite).sorted(key=lambda x: x.id, reverse=True)[:1]
                name = tramite.tipo_tramite_id.name.replace(' ', '_')
                doc = vehiculo._helper_build_doc_dict(
                    tramite, 'expediente', name, type='with_data'
                )
                if doc:
                    tramites_list.append(doc)
            if archivo.startswith('adecuacion'):
                tipo_adecuacion = archivo.split(":", 1)[1].strip()
                adecuacion = vehiculo.adecuacion_ids.filtered(lambda x: x.adecuacion_id.name == tipo_adecuacion).sorted(key=lambda x: x.id, reverse=True)[:1]
                name = adecuacion.adecuacion_id.name.replace(' ', '_')
                doc = vehiculo._helper_build_doc_dict(
                    adecuacion,
                    'expediente_arch',
                    name,
                    type='with_data'
                )
                if doc:
                    adecuaciones_list.append(doc)
        return {
            'factura': factura_data,
            'opcion_compra': opcion_compra_data,
            'adecuaciones': adecuaciones_list or None,
            'tramites': tramites_list or None,
            'contrato': contrato_data,
            'polizas': polizas_list if polizas_list else None,
            'faltantes': faltantes,
            'completo': validacion['completo'],
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
        tipo = self.env['fleet.poliza.tipo'].search([('name', '=', nombre_tipo)],limit=1)
        if not tipo:
            return self.env['fleet.poliza']
        polizas = self.poliza_ids.filtered(
            lambda p: (
                    p.tipo_poliza_id == tipo
                    and p.fecha_vencimiento
                    and p.fecha_vencimiento >= fields.Date.today()
            )
        )
        return polizas.sorted(key=lambda p: p.id)[-1:]

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
        sheet.write(0, 1, 'Plaza', header_format)
        sheet.write(0, 2, 'Etapa', header_format)
        sheet.write(0, 3, 'Sub etapa', header_format)
        sheet.write(0, 4, 'Estado', header_format)
        sheet.write(0, 5, 'Días incompleto', header_format)
        sheet.write(0, 6, 'Faltantes', header_format)
        sheet.set_column(0, 0, 22)
        sheet.set_column(1, 1, 14)
        sheet.set_column(2, 2, 14)
        sheet.set_column(3, 3, 14)
        sheet.set_column(4, 4, 14)
        sheet.set_column(5, 5, 14)
        sheet.set_column(6, 6, 14)
        sheet.freeze_panes(1, 0)
        for fila, resultado in enumerate(resultados, start=1):
            es_completo = resultado['expediente'] == 'completo'
            sheet.write(fila, 0, resultado['vehiculo'] or '')
            sheet.write(fila, 1, resultado['plaza'] or '')
            sheet.write(fila, 2, resultado['etapa'] or '')
            sheet.write(fila, 3, resultado['sub_etapa'] or '')
            sheet.write(fila, 4, resultado['expediente'].capitalize(), ok_format if es_completo else bad_format)
            sheet.write(fila, 5, resultado['dias_incompleto'] or 0)
            for i, record in enumerate(resultado['faltantes']):
                columna = 6 + i
                sheet.set_column(
                    columna,
                    columna,
                    max(len(record['faltante']) + 2, 35)
                )
                sheet.write(fila, columna, record['faltante'], wrap_format)
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