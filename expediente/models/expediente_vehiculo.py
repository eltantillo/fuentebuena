import base64
import io
import logging
import zipfile


from odoo import api, fields, models
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

_logger = logging.getLogger(__name__)


class ExpedienteVehiculo(models.Model):
    _inherit = 'fleet.vehicle'

    dias_expe_incompleto = fields.Integer(string='Días de incompleto')

    def validar_factura(self):
        if not self.existe_factura:
            return {'faltante': 'Factura', 'motivo': 'falta subir'}
        return None

    def validar_opcion_compra(self):
        if not self.existe_opcion_compra:
            return {'faltante': 'Opción a compra', 'motivo': 'falta subir'}
        return None

    def validar_contrato(self, contrato):
        if not contrato or not contrato.existe_attach_contrato:
            return {'faltante': 'Contrato', 'motivo': 'falta subir'}

        today = fields.Date.today()
        if contrato.state != 'open' or (contrato.expiration_date and contrato.expiration_date < today):
            return {'faltante': 'Contrato', 'motivo': 'vencido'}

        return None

    def validar_tramite(self, tramite, tramite_req):
        if not tramite or not tramite.existe_expediente:
            return {'faltante': tramite_req, 'motivo': 'falta subir'}

        if tramite.tipo_tramite_id.notificar_renovacion:
            today = fields.Date.today()
            if not tramite.fecha_vencimiento_renovacion or tramite.fecha_vencimiento_renovacion < today:
                return {'faltante': tramite_req, 'motivo': 'vencido'}

        return None

    def validar_adecuacion(self, adecuacion, adecuacion_req):
        if not adecuacion or not adecuacion.existe_expediente_arch:
            return {'faltante': f'Adecuación: {adecuacion_req}', 'motivo': 'falta subir'}
        return None

    def validar_poliza(self, poliza):
        if not poliza or not poliza.existe_attach_poliza:
            return {'faltante': 'Póliza', 'motivo': 'falta subir'}

        today = fields.Date.today()
        if not poliza.fecha_vencimiento or poliza.fecha_vencimiento < today:
            return {'faltante': 'Póliza', 'motivo': 'vencido'}

        return None

    def return_inexistencia(self, faltante):
        return {'faltante': faltante, 'motivo': 'sin registro'}

    def check_expediente_completo(self, expediente_tipo, poliza_map=None, endoso_map=None,
        tramites_map=None, adecuaciones_map=None, contrato=None):
        self.ensure_one()
        faltantes = []
        completos = []
        if expediente_tipo.factura_req:
            res = self.validar_factura()
            faltantes.append(res) if res else completos.append({'completo': 'Factura', 'motivo': 'vigente'})
        if expediente_tipo.opcion_compra_req:
            res = self.validar_opcion_compra()
            faltantes.append(res) if res else completos.append({'completo': 'Opción a compra', 'motivo': 'vigente'})
        if expediente_tipo.poliza_req:
            poliza = poliza_map.get(self.id) if poliza_map is not None else None
            if poliza:
                res = self.validar_poliza(poliza)
                faltantes.append(res) if res else completos.append({'completo': 'Póliza', 'motivo': 'vigente'})
            else:
                faltantes.append(self.return_inexistencia('Póliza'))
        if expediente_tipo.endoso_req:
            endoso = endoso_map.get(self.id) if endoso_map is not None else None
            if not endoso:
                faltantes.append(self.return_inexistencia('Endoso'))
            elif endoso.existe_attach_poliza:
                completos.append({'completo': 'Endoso', 'motivo': 'vigente'})
            else:
                faltantes.append({'faltante': 'Endoso', 'motivo': 'falta subir'})
        if expediente_tipo.contrato_req:
            if self.state_id.name == 'Rentado':
                res = self.validar_contrato(contrato)
                faltantes.append(res) if res else completos.append({'completo': 'Contrato', 'motivo': 'vigente'})

        tramites_vehiculo = tramites_map.get(self.id, {}) if tramites_map is not None else {}
        for tramite_req in expediente_tipo.tipo_tramite_ids:
            if self.plaza_id.id in tramite_req.plaza_ids.ids:
                tramite = tramites_vehiculo.get(tramite_req.id)
                if tramite:
                    res = self.validar_tramite(tramite, tramite_req.name)
                    faltantes.append(res) if res else completos.append({'completo': tramite_req.name, 'motivo': 'vigente'})
                elif tramite_req.name != 'Dictamen anual GNV' or self.es_gnv:
                    faltantes.append(self.return_inexistencia(tramite_req.name))
        adecuaciones_vehiculo = adecuaciones_map.get(self.id, {}) if adecuaciones_map is not None else {}
        for adecuacion_req in expediente_tipo.tipo_adecuacion_ids:
            adecuacion = adecuaciones_vehiculo.get(adecuacion_req.id)
            if adecuacion:
                res = self.validar_adecuacion(adecuacion, adecuacion_req.name)
                faltantes.append(res) if res else completos.append(
                    {'completo': f'Adecuación: {adecuacion_req.name}', 'motivo': 'vigente'})
            elif adecuacion_req.name != 'GNV' or self.es_gnv:
                faltantes.append(self.return_inexistencia(f'Adecuación: {adecuacion_req.name}'))
        return {
            'completo': len(faltantes) == 0,
            'faltantes': faltantes,
            'completos': completos
        }

    def _build_prefetch_maps(self, expediente_tipo):
        poliza_map = {}
        endoso_map = {}
        if expediente_tipo.poliza_req or expediente_tipo.endoso_req:
            todas_polizas = self.mapped('poliza_ids')
            todas_polizas.mapped('tipo_poliza_id.name')
            todas_polizas.mapped('existe_attach_poliza')
            todas_polizas.mapped('fecha_vencimiento')
            for vehiculo in self:
                polizas_v = vehiculo.poliza_ids.filtered(lambda p: p.tipo_poliza_id.name == 'Póliza').sorted(
                    'id', reverse=True)
                if polizas_v:
                    poliza_map[vehiculo.id] = polizas_v[0]
                endosos_v = vehiculo.poliza_ids.filtered(lambda p: p.tipo_poliza_id.name == 'Endoso').sorted(
                    'id', reverse=True)
                if endosos_v:
                    endoso_map[vehiculo.id] = endosos_v[0]
        tramites_map = {}
        if expediente_tipo.tipo_tramite_ids:
            todos_tramites = self.mapped('tramite_ids')
            todos_tramites.mapped('tipo_tramite_id.notificar_renovacion')
            todos_tramites.mapped('existe_expediente')
            todos_tramites.mapped('fecha_vencimiento_renovacion')
            for vehiculo in self:
                por_tipo = {}
                for t in vehiculo.tramite_ids.sorted('id', reverse=True):
                    por_tipo.setdefault(t.tipo_tramite_id.id, t)
                tramites_map[vehiculo.id] = por_tipo
        adecuaciones_map = {}
        if expediente_tipo.tipo_adecuacion_ids:
            todas_adecuaciones = self.mapped('adecuacion_ids')
            todas_adecuaciones.mapped('adecuacion_id.name')
            todas_adecuaciones.mapped('existe_expediente_arch')
            for vehiculo in self:
                por_tipo = {}
                for a in vehiculo.adecuacion_ids.sorted('id', reverse=True):
                    por_tipo.setdefault(a.adecuacion_id.id, a)
                adecuaciones_map[vehiculo.id] = por_tipo
        contrato_map = {}
        if expediente_tipo.contrato_req:
            self.mapped('log_contracts.existe_attach_contrato')
            self.mapped('log_contracts.state')
            self.mapped('log_contracts.expiration_date')
            for vehiculo in self:
                contrato_map[vehiculo.id] = vehiculo.get_contrato_record()
        return poliza_map, endoso_map, tramites_map, adecuaciones_map, contrato_map

    @api.model
    def return_validacion_expe_paginado(self, domain, expediente_id, page=1, limit=25):
        offset = (page - 1) * limit
        total_count = self.search_count(domain)
        vehiculos = self.search(domain, offset=offset, limit=limit)
        expediente_tipo = self.env['expediente.tipo'].browse(expediente_id)
        resultado = []
        poliza_map, endoso_map, tramites_map, adecuaciones_map, contrato_map = \
            vehiculos._build_prefetch_maps(expediente_tipo)
        for vehiculo in vehiculos:
            validacion = vehiculo.check_expediente_completo(expediente_tipo,
            poliza_map=poliza_map,
            endoso_map=endoso_map,
            tramites_map=tramites_map,
            adecuaciones_map=adecuaciones_map,
            contrato=contrato_map.get(vehiculo.id),
            )
            resultado.append({
                'id': vehiculo.id,
                'vehiculo': vehiculo.vin_sn or '',
                'license_plate': vehiculo.license_plate or '',
                'dias_incompleto': vehiculo.dias_expe_incompleto,
                'plaza': vehiculo.plaza_id.name or '',
                'etapa': vehiculo.state_id.name or '',
                'sub_etapa': vehiculo.sub_etapa_id.name or '',
                'expediente': validacion['completo'],
                'faltantes': validacion['faltantes'],
                'completos': validacion['completos'],
            })
        return {
            'records': resultado,
            'total': total_count,
        }

    @api.model
    def return_validacion_expe(self, vehiculos, tipo_expe, context=''):
        vehiculos_recs = self.browse(vehiculos).exists()
        tipo_expediente = self.env['expediente.tipo'].browse(tipo_expe) if isinstance(tipo_expe, int) else tipo_expe
        vehiculos_recs.mapped('vin_sn')
        vehiculos_recs.mapped('license_plate')
        vehiculos_recs.mapped('plaza_id.name')
        vehiculos_recs.mapped('state_id.name')
        vehiculos_recs.mapped('sub_etapa_id.name')
        poliza_map, endoso_map, tramites_map, adecuaciones_map, contrato_map = \
            vehiculos_recs._build_prefetch_maps(tipo_expediente)
        resultado = []
        for vehiculo in vehiculos_recs:
            validacion = vehiculo.check_expediente_completo(
                tipo_expediente,
                poliza_map=poliza_map,
                endoso_map=endoso_map,
                tramites_map=tramites_map,
                adecuaciones_map=adecuaciones_map,
                contrato=contrato_map.get(vehiculo.id),
            )
            if context == 'cron_job' and validacion['faltantes'] and tipo_expediente.expediente_principal:
                vehiculo.dias_expe_incompleto += 1
            elif context == 'cron_job' and not validacion['faltantes'] and tipo_expediente.expediente_principal:
                vehiculo.dias_expe_incompleto = 0
            resultado.append({
                'id': vehiculo.id,
                'vehiculo': vehiculo.vin_sn or '',
                'license_plate': vehiculo.license_plate or '',
                'dias_incompleto': vehiculo.dias_expe_incompleto,
                'plaza': vehiculo.plaza_id.name or '',
                'etapa': vehiculo.state_id.name or '',
                'sub_etapa': vehiculo.sub_etapa_id.name or '',
                'expediente': validacion['completo'],
                'faltantes': validacion['faltantes'],
                'completos': validacion['completos'],
            })
        return resultado

    def _helper_build_doc_dict(self, record, binary_field_name, default_name, type="without_data", name=""):
        if not record:
            return None
        vin = self.vin_sn or 'SIN_VIN'
        vals = {
            'id': record.id,
            'name': name,
            'doc_name': f"{default_name}_{vin}.pdf"
        }
        if name == 'Póliza':
            vals['fecha_vencimiento'] = record.fecha_vencimiento
        if hasattr(record, 'tipo_tramite_id') and record.tipo_tramite_id:
            if record.tipo_tramite_id.notificar_renovacion:
                vals['fecha_vencimiento'] = record.fecha_vencimiento_renovacion
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

    def get_contrato_record(self):
        self.ensure_one()
        return self.log_contracts[-1] if self.log_contracts else None

    def get_factura(self, type="without_data"):
        self.ensure_one()
        return self._helper_build_doc_dict(self, 'factura_vehiculo', 'factura',
                                           type=type, name='Factura') if self.existe_factura else None

    def get_opcion_compra(self, type="without_data"):
        self.ensure_one()
        return self._helper_build_doc_dict(self, 'opcion_compra', 'opcion_compra',
                                           type=type, name='Opción a compra') if self.existe_opcion_compra else None

    def get_contrato(self, type="without_data"):
        self.ensure_one()
        contrato = self.get_contrato_record()
        return self._helper_build_doc_dict(contrato, 'attach_contrato', 'contrato',
                                           type=type, name='Contrato') if contrato and contrato.existe_attach_contrato else None

    def get_polizas(self, type="without_data"):
        self.ensure_one()
        res = [self._helper_build_doc_dict(p, 'attach_poliza', p.tipo_poliza_id.name or 'poliza', type=type, name=p.tipo_poliza_id.name)
               for p in self.poliza_ids.filtered('existe_attach_poliza')]
        return [d for d in res if d] or None

    def get_adecuaciones(self, type="without_data"):
        self.ensure_one()
        res = [
            self._helper_build_doc_dict(a, 'expediente_arch', (a.adecuacion_id.name or 'adecuacion').replace(' ', '_'),
                                        type=type, name=a.adecuacion_id.name)
            for a in self.adecuacion_ids.filtered('existe_expediente_arch')]
        return [d for d in res if d] or None

    def get_tramites(self, type="without_data"):
        self.ensure_one()
        res = [self._helper_build_doc_dict(t, 'expediente', (t.tipo_tramite_id.name or 'tramite').replace(' ', '_'),
                                           type=type, name=t.tipo_tramite_id.name)
               for t in self.tramite_ids.filtered('existe_expediente')]
        return [d for d in res if d] or None

    @api.model
    def get_expediente_type(self, expediente_tipo_id, vehiculo_id):
        tipos_tramite = self.env['fleet.tramite.tipo'].search([]).mapped('name')
        vehiculo = self.browse(vehiculo_id)
        if not vehiculo.exists():
            return None
        expediente = self.env['expediente.tipo'].browse(expediente_tipo_id)
        poliza_map, endoso_map, tramites_map, adecuaciones_map, contrato_map = \
            vehiculo._build_prefetch_maps(expediente)
        validacion = vehiculo.check_expediente_completo(expediente,
        poliza_map=poliza_map,
        endoso_map=endoso_map,
        tramites_map=tramites_map,
        adecuaciones_map=adecuaciones_map,
        contrato=contrato_map.get(vehiculo.id),
        )
        polizas_list = []
        tramites_list = []
        adecuaciones_list = []
        for archivo in validacion['completos']:
            if archivo['completo'] == 'Póliza' or archivo['completo'] == 'Endoso':
                tipo_nombre = 'Póliza' if archivo['completo'] == 'Póliza' else 'Endoso'
                rec = vehiculo.poliza_ids.filtered(lambda p: p.tipo_poliza_id.name == tipo_nombre).sorted('id',reverse=True)[:1]
                doc = vehiculo._helper_build_doc_dict(rec, 'attach_poliza', tipo_nombre.lower(), type='with_data', name=tipo_nombre)
                if doc: polizas_list.append(doc)
            elif archivo['completo'] in tipos_tramite:
                tipo = archivo['completo']
                rec = vehiculo.tramite_ids.filtered(lambda x: x.tipo_tramite_id.name == tipo).sorted('id',reverse=True)[:1]
                doc = vehiculo._helper_build_doc_dict(rec, 'expediente', tipo.replace(' ', '_'), type='with_data', name=tipo)
                if doc: tramites_list.append(doc)
            elif archivo['completo'].startswith('Adecuación:'):
                tipo = archivo['completo'].split(":", 1)[1].strip()
                rec = vehiculo.adecuacion_ids.filtered(lambda x: x.adecuacion_id.name == tipo).sorted('id',reverse=True)[:1]
                doc = vehiculo._helper_build_doc_dict(rec, 'expediente_arch', tipo.replace(' ', '_'), type='with_data', name=f'Adecuación: {tipo}')
                if doc: adecuaciones_list.append(doc)
        return {
            'factura': vehiculo.get_factura(type='with_data')if any(item.get('completo') == 'Factura' for item in validacion['completos']) else None,
            'opcion_compra': vehiculo.get_opcion_compra(type='with_data')if any(item.get('completo') == 'Opción a compra' for item in validacion['completos']) else None,
            'contrato': vehiculo.get_contrato(type='with_data') if any(item.get('completo') == 'Contrato' for item in validacion['completos']) else None,
            'adecuaciones': adecuaciones_list or None,
            'tramites': tramites_list or None,
            'polizas': polizas_list or None,
            'faltantes': validacion['faltantes'],
            'completo': validacion['completo'],
        }

    @api.model
    def get_zip_expediente(self, vehiculo_id, tipo_expediente=None):
        vehiculo = self.browse(vehiculo_id)
        if not vehiculo.exists():
            return None
        expediente = vehiculo.get_expediente_type(tipo_expediente, vehiculo.id) if tipo_expediente else {
            'factura': vehiculo.get_factura(type='with_data'),
            'opcion_compra': vehiculo.get_opcion_compra(type='with_data'),
            'contrato': vehiculo.get_contrato(type='with_data'),
            'polizas': vehiculo.get_polizas(type='with_data'),
            'tramites': vehiculo.get_tramites(type='with_data'),
            'adecuaciones': vehiculo.get_adecuaciones(type='with_data'),
        }
        documentos = []
        for clave in ('factura', 'opcion_compra', 'contrato'):
            if expediente.get(clave):
                documentos.append(expediente[clave])
        for clave in ('polizas', 'tramites', 'adecuaciones'):
            if expediente.get(clave):
                documentos.extend(expediente[clave])
        if not documentos:
            return None
        buffer = io.BytesIO()
        nombres_usados = {}
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archivo_zip:
            for doc in documentos:
                if not doc.get('data'):
                    continue
                nombre = doc['doc_name']
                nombres_usados[nombre] = nombres_usados.get(nombre, 0) + 1
                if nombres_usados[nombre] > 1:
                    base, _, ext = nombre.rpartition('.')
                    nombre = f"{base}_{nombres_usados[nombre]}.{ext or 'pdf'}"

                archivo_zip.writestr(nombre, base64.b64decode(doc['data']))

        buffer.seek(0)
        return {
            'name': f"expediente_{vehiculo.vin_sn or 'SIN_VIN'}.zip",
            'data': base64.b64encode(buffer.read()).decode('utf-8'),
            'mimetype': 'application/zip',
        }

    @api.model
    def get_faltantes_excel(self, vehiculos, tipo_expe, estado=False, context=False):
        if xlsxwriter is None:
            raise UserError("El módulo 'xlsxwriter' no está instalado en el servidor.")
        resultados = self.return_validacion_expe(vehiculos, tipo_expe, context)
        if estado:
            bool_estado = True if estado == 'completo' else False
            resultados = [r for r in resultados if r['expediente'] == bool_estado]
        expediente_tipo = self.env['expediente.tipo'].browse(tipo_expe)
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        sheet = workbook.add_worksheet('Expedientes')
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#263D3D', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        ok_format = workbook.add_format({'font_color': '#00B377', 'bold': True})
        bad_format = workbook.add_format({'font_color': '#FF2D55', 'bold': True})
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        headers = ['VIN', 'Plaza', 'Etapa', 'Sub etapa', 'Estado', 'Días incompleto', 'Faltantes']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, header_format)
            sheet.set_column(col, col, 18)
        sheet.freeze_panes(1, 0)
        for fila, r in enumerate(resultados, start=1):
            sheet.write(fila, 0, r['vehiculo'])
            sheet.write(fila, 1, r['plaza'])
            sheet.write(fila, 2, r['etapa'])
            sheet.write(fila, 3, r['sub_etapa'])
            sheet.write(fila, 4, 'Completo' if r['expediente'] else 'Incompleto',
                        ok_format if r['expediente'] else bad_format)
            sheet.write(fila, 5, r['dias_incompleto'])

            for i, record in enumerate(r['faltantes']):
                col = 6 + i
                sheet.write(fila, col, f"{record['faltante']} ({record['motivo']})", wrap_format)
        workbook.close()
        buffer.seek(0)
        nombre_tipo = (expediente_tipo.name or 'expediente').replace(' ', '_')
        return {
            'name': f'faltantes_{nombre_tipo}.xlsx',
            'data': base64.b64encode(buffer.read()).decode('utf-8'),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }

    @api.model
    def _cron_notificar_expedientes(self):
        tipos = self.env['expediente.tipo'].search([('notificar_por_correo', '=', True)])
        etapa_baja = self.env['fleet.vehicle.state'].search([('es_etapa_baja', '=', True)], limit=1)
        domain = [('flotilla_id', '=', 1)]
        if etapa_baja:
            domain.append(('state_id', '!=', etapa_baja.id))
        vehiculos_ids = self.search(domain).ids
        for tipo in tipos:
            emails = list({u.work_email for u in tipo.usuarios_notificar_ids if u.work_email})
            if not emails:
                continue
            excel = self.get_faltantes_excel(vehiculos_ids, tipo.id, 'incompleto', 'cron_job')
            if not excel:
                continue
            attachment = self.env['ir.attachment'].sudo().create({
                'name': excel['name'],
                'type': 'binary',
                'datas': excel['data'],
                'mimetype': excel['mimetype'],
            })
            try:
                mail = self.env['mail.mail'].sudo().create({
                    'subject': f'Estado de expedientes - {tipo.name}',
                    'body_html': f"""
                        <p>Buen día,</p>
                        <p>Se adjunta el reporte correspondiente al expediente <b>{tipo.name}</b>.</p>
                        <p>Saludos.</p>
                    """,
                    'email_to': ','.join(emails),
                    'attachment_ids': [(4, attachment.id)],
                })
                mail.send()
            except Exception as e:
                _logger.error(f"Error enviando correo de expediente {tipo.name}: {e}")