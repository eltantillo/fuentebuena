from odoo import fields, models, api
import logging
import time
import json
import requests
import random
import pytz
import ast
import re
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)
_logger.info("Cargando modelo CMConectorSimplyBook...")


class CMConectorSimplyBook(models.Model):
    _inherit = 'cita.mantenimiento'

    simplybook_id = fields.Integer(
        string='Simply Book ID',
        tracking=True,
    )
    name_simplybook = fields.Char(
        string='Nombre en SimplyBook',
    )
    correo_simplybook = fields.Char(
        string='Correo en SimplyBook',
    )
    telefono_simplybook = fields.Char(
        string='Teléfono en SimplyBook',
    )
    odometro_simplybook = fields.Integer(
        string='Odometro en SimplyBook',
    )
    entity_raw = fields.Text(
        string='Cuerpo JSON'
    )

    def model_update(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cita.mantenimiento',
            'res_id': self.id,
            'name': 'Actualizar datos',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('cita_mantenimiento.confirmar_update_view_form').id,
        }

    def update_datos(self):
        self.ensure_one()
        cliente = self.cliente_id.sudo()
        cliente.write({
            'email': self.correo_simplybook,
            'phone': self.telefono_simplybook,
        })
        self.sudo().write({
            'correo_cliente': self.correo_simplybook,
            'telefono_cliente': self.telefono_simplybook,
        })

    def return_etapa_mante(self, name):
        etapa = self.env['fleet.mantenimiento.etapa'].search([('name', '=', name)])
        return etapa

    def return_tipo_mante(self, name):
        tipo = self.env['fleet.mantenimiento.tipo'].search([('name', '=', name)])
        return tipo

    def return_orig_creacion(self, name):
        tipo = self.env['fleet.catalogo.orig.creacion'].search([('name', '=', name)])
        return tipo

    def convertir_a_hora_local(self, fecha):
        zona_local = pytz.timezone('America/Mexico_City')
        fecha_utc = pytz.utc.localize(fecha)
        return fecha_utc.astimezone(zona_local)

    def autenticar(self):
        _logger.info("Iniciando proceso de autenticación con SimplyBook...")
        url = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.auth')
        login = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.login')
        password = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.password')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        json_body = {
            "company": "pilotea",
            "login": login,
            "password": password
        }
        _logger.debug("Enviando petición POST a %s para autenticar", url)
        response = requests.request("POST", url, json=json_body, headers=headers)
        if response.ok:
            data = response.json()
            token = data['token']
            refresh_token = data['refresh_token']
            self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.token', token)
            self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.refresh_token', refresh_token)
            _logger.info("Autenticación exitosa. Tokens actualizados.")
            return data
        else:
            _logger.error("Fallo en la autenticación. Status: %s, Respuesta: %s", response.status_code, response.text)
            return False

    def _renovar_token(self):
        _logger.info("Intentando renovar token...")
        refresh_url = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.url_refresh_token')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        body = {
            "company": "pilotea",
            "refresh_token": self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.refresh_token'),
        }
        response = requests.post(refresh_url, json=body, headers=headers)
        if response.ok:
            data = response.json()
            self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.token', data['token'])
            self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.refresh_token', data['refresh_token'])
            _logger.info("Token renovado exitosamente.")
            return data
        if response.status_code == 401:
            _logger.warning("Refresh token inválido o expirado (401). Forzando re-autenticación completa.")
            self.autenticar()
            return False

    def return_headers(self):
        _logger.debug("Construyendo headers para la petición...")
        return {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'X-Company-Login': "pilotea",
            'X-Token': self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.token'),
        }

    def helper_request(self, method, url, **kwargs):
        _logger.info("Ejecutando helper_request: [%s] %s", method, url)
        headers = self.return_headers()
        response = requests.request(
            method,
            url,
            headers=headers,
            timeout=(10, 30),
            **kwargs
        )
        time.sleep(1)
        if response.ok:
            _logger.debug("helper_request exitoso (Status: %s)", response.status_code)
            return response
        if response.status_code == 401:
            _logger.info("Token expirado (401) en helper_request. Renovando token y reintentando...")
            self._renovar_token()
            _logger.info("Reintentando la petición HTTP con el nuevo token...")
            headers_nuevos = self.return_headers()  # Volvemos a pedir los headers para que jale el nuevo token de la BD
            response = requests.request(
                method,
                url,
                headers=headers_nuevos,
                timeout=(10, 30),
                **kwargs
            )
            time.sleep(1)
        elif response.status_code == 429:
            _logger.warning("🚨 Rate limit alcanzado (429) en url: %s", url)
            raise Exception("Error 429")
        _logger.error("Error en helper_request [%s]. Respuesta: %s", response.status_code, response.text)
        return response

    def get_book_details(self, url):
        _logger.info("Obteniendo detalles de reserva desde: %s", url)
        response = self.helper_request("GET", url)
        if response.ok:
            _logger.info("Respuesta exitosa recibida de %s (Status: %s)", url, response.status_code)
            try:
                return response.json()
            except Exception as e:
                _logger.error("Error al parsear el JSON de la respuesta de %s: %s", url, e)
                return False
        else:
            _logger.error(
                "Falló la petición a la URL: %s. Status code: %s - Detalles del error: %s",
                url, response.status_code, response.text
            )
            return False

    def _convertir_a_utc(self, fecha_str):
        _logger.debug("Convirtiendo fecha a UTC: %s", fecha_str)
        zona_local = pytz.timezone('America/Mexico_City')
        fecha_naive = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        fecha_local = zona_local.localize(fecha_naive)
        fecha_utc = fecha_local.astimezone(pytz.utc)
        fecha_final = fecha_utc.replace(tzinfo=None)
        _logger.debug("Fecha UTC resultante: %s", fecha_final)
        return fecha_final

    def individual_books(self, id_books):
        _logger.info("🔍 == INICIO individual_books == ID recibido: %s", id_books)
        matricula = ''
        odometro = 0
        url = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.book_details')
        _logger.info("🌐 URL base obtenida desde parámetros: %s", url)
        url_construct = f"{url.rstrip('/')}/{int(id_books)}"
        _logger.info("📡 URL construida para consulta: %s", url_construct)
        respuesta = self.get_book_details(url_construct)
        _logger.info("📥 Respuesta recibida desde get_book_details: %s", respuesta)
        if respuesta:
            _logger.info("✅ Respuesta válida encontrada para booking ID: %s", id_books)
            aditional_fields = respuesta['additional_fields']
            _logger.info("🧾 Additional fields encontrados: %s", aditional_fields)
            for record in aditional_fields:
                _logger.info("🔄 Procesando additional field: %s", record)
                if 'placas' in (record.get('field_name' or '').lower()):
                    matricula = record['value'] if record.get('value') else ''
                    _logger.info("🚗 Matrícula detectada: %s", matricula)
                if 'kilometraje' in (record.get('field_name' or '').lower()):
                    odometro = record['value'] if record.get('value') else ''
                    _logger.info("🛞 Odómetro detectado: %s", odometro)
            start_date = respuesta['start_datetime']
            end_date = respuesta['end_datetime']
            _logger.info("📅 Fecha inicio obtenida: %s", start_date)
            _logger.info("📅 Fecha fin obtenida: %s", end_date)
            proveedor_odoo = self.env['res.partner'].search([
                ('simplybook_proveedor_id', '=', respuesta['provider_id'])
            ], limit=1)
            _logger.info(
                "🏢 Resultado búsqueda proveedor Odoo con provider_id %s: %s",
                respuesta['provider_id'],
                proveedor_odoo
            )
            prov_odoo_id = proveedor_odoo.id
            _logger.info("🆔 ID proveedor Odoo encontrado: %s", prov_odoo_id)
            data = {
                'odometro': odometro,
                'proveedor_id': prov_odoo_id,
                'simplybook_id': id_books,
                'matricula': matricula,
                'start_date': start_date,
                'end_date': end_date,
                'name_simplybook': respuesta['client']['name'],
                'correo_simplybook': respuesta['client']['email'],
                'telefono_simplybook': respuesta['client']['phone'].replace("+52", ""),
                'json_raw': respuesta
            }
            _logger.info("📦 Diccionario final construido en individual_books: %s", data)
            _logger.info("🏁 == FIN individual_books EXITOSO == ID: %s", id_books)
            return data
        else:
            _logger.warning(
                "⚠️ No se obtuvo respuesta válida desde get_book_details para booking ID: %s",
                id_books
            )
            _logger.info("🏁 == FIN individual_books FALLIDO == ID: %s", id_books)
            return False

    def provider_list(self):
        _logger.info("Iniciando provider_list para obtener todos los proveedores de SimplyBook")
        url = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.provider_list')
        all_data = []
        current_page = 1
        total_pages = 1
        metadata = {}
        while current_page <= total_pages:
            _logger.debug("Consultando página %s de proveedores...", current_page)
            response = self.helper_request("GET", f"{url}?page={current_page}")
            json_response = response.json()
            data = json_response.get('data', [])
            metadata = json_response.get('metadata', {})
            all_data.extend(data)
            total_pages = metadata.get('pages_count', 1)
            _logger.debug("Página %s procesada. Proveedores en esta página: %s", current_page, len(data))
            current_page += 1
        master_json = {
            'data': all_data,
            'metadata': {
                'items_count': len(all_data),
                'pages_count': total_pages
            }
        }
        _logger.info("Fin provider_list. Total de proveedores obtenidos: %s", len(all_data))
        return master_json

    def process_cita_save(self, id_books):
        _logger.info("Agregando a cola (crear) para id_books: %s", id_books)
        res = self.env['cm.conector.simply.cola'].create({
            'booking_id': id_books,
            'state': 'pendiente',
            'operation_type': 'crear',
        })
        _logger.debug("Registro de cola creado con ID: %s", res.id)
        return res

    def cancel_cita_save(self, id_books):
        _logger.info("Agregando a cola (cancelar) para id_books: %s", id_books)
        res = self.env['cm.conector.simply.cola'].create({
            'booking_id': id_books,
            'state': 'pendiente',
            'operation_type': 'cancelar',
        })
        _logger.debug("Registro de cola creado con ID: %s", res.id)
        return res

    def update_cita_save(self, id_books):
        _logger.info("Agregando a cola (actualizar) para id_books: %s", id_books)
        res = self.env['cm.conector.simply.cola'].create({
            'booking_id': id_books,
            'state': 'pendiente',
            'operation_type': 'actualizar',
        })
        _logger.debug("Registro de cola creado con ID: %s", res.id)
        return res

    def process_cita(self, id_books):
        _logger.info("== INICIO process_cita para id_books: %s ==", id_books)
        etapa_programado = self.env['fleet.mantenimiento.etapa'].search([('name', '=', 'Programado')], limit=1)
        data = self.individual_books(id_books)
        if not data:
            _logger.warning("No se obtuvieron datos desde individual_books para id_books: %s. Abortando process_cita.",
                            id_books)
            raise Exception("No se recibio data valida")

        _logger.debug("Construyendo diccionario principal de la cita...")
        etapa_requerido = self.return_etapa_mante('Requerido')
        tipo_mantenimiento = self.return_tipo_mante('Vehicular Preventivo')
        diccionario = {
            'proveedor_id': data.get('proveedor_id'),
            'entity_raw': str(data),
            'fecha_cita_inicio': self._convertir_a_utc(data.get('start_date')),
            'fecha_cita_fin': self._convertir_a_utc(data.get('end_date')),
            'simplybook_id': int(data.get('simplybook_id', 0)),
            'etapa_id': 1,
            'name_simplybook': data.get('name_simplybook'),
            'correo_simplybook': data.get('correo_simplybook'),
            'telefono_simplybook': data.get('telefono_simplybook'),
            'odometro_simplybook': data.get('odometro'),
        }
        matricula = data.get('matricula')
        matricula = matricula.upper()
        llave = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.llave_creacion')
        if llave in matricula:
            matricula = matricula.replace("-MTTO","")
        _logger.info("Buscando vehículo en Odoo con matrícula: %s", matricula)
        vehiculo = self.env['fleet.vehicle'].search([('license_plate', '=', matricula)], limit=1)
        if vehiculo:
            _logger.info("Vehículo encontrado: %s", vehiculo.name)
            odometro = vehiculo.odometro_mod
            diccionario['vehiculo_id'] = vehiculo.id
            cliente_id = vehiculo.driver_id.id
            if cliente_id:
                diccionario['cliente_id'] = cliente_id

            _logger.info("Buscando mantenimiento preventivo requerido para el vehículo...")
            mantenimiento = self.env['fleet.mantenimiento'].search([
                ('vehiculo_id', '=', vehiculo.id),
                ('etapa_id', 'in', [etapa_requerido.id, etapa_programado.id]),
                ('tipo_mantenimiento_id', '=', tipo_mantenimiento.id)
            ], limit=1)

            if mantenimiento:
                _logger.info("Mantenimiento encontrado (ID: %s). Actualizando etapa y fecha...", mantenimiento.id)
                mantenimiento.etapa_id = etapa_requerido.id
                mantenimiento.fecha_programado = fields.Date.today()
                mantenimiento.proveedor_id = diccionario['proveedor_id']
                cita_vinculada = self.search([('mantenimiento_id', '=', mantenimiento.id)], limit=1)
                if cita_vinculada:
                    _logger.info("Se encontró una cita ya vinculada (ID: %s). Procesando reagenda...",
                                 cita_vinculada.id)
                    etapa_reagenda = self.env['cita.mantenimiento.etapa'].search([('name', '=', 'Reagendada')], limit=1)
                    diccionario['etapa_id'] = etapa_reagenda.id
                    if cita_vinculada.simplybook_id:
                        self.cancel_cita_save(cita_vinculada.simplybook_id)
                    cita_vinculada.contador_reagenda += 1
                    cita_vinculada.write(diccionario)
                    _logger.info("Cita existente actualizada exitosamente.")
                else:
                    _logger.info("No se encontró cita vinculada. Creando nueva cita vinculada al mantenimiento...")
                    diccionario['mantenimiento_id'] = mantenimiento.id
                    nueva_cita = self.env['cita.mantenimiento'].create(diccionario)
                    _logger.info("Nueva cita creada: ID %s", nueva_cita.id)
            else:
                _logger.info("No existe mantenimiento previo. Se procederá a crear uno de forma automática.")
                valor = self.env['fleet.vehicle']._redondear(odometro)
                if valor == 0:
                    valor = 10000
                mantenimiento_proximo_id = self.env['fleet.mantenimiento.servicio.tipo'].search([
                    ('mantenimiento_tipo_id', '=', tipo_mantenimiento.id),
                    ('valor', '=', valor),
                ], limit=1)
                origen_creacion = self.return_orig_creacion('Automatico')
                dict_mante = {
                    'proveedor_id': diccionario['proveedor_id'],
                    'etapa_id': etapa_requerido.id,
                    'origen_id': origen_creacion.id,
                    'tipo_mantenimiento_id': tipo_mantenimiento.id,
                    'tipo_mantenimiento_servicio_id': mantenimiento_proximo_id.id,
                    'vehiculo_id': vehiculo.id,
                    'fecha_deteccion': fields.Date.today(),
                    'km_deteccion': odometro,
                }
                nuevo_mante = self.env['fleet.mantenimiento'].create_custom(dict_mante)
                nuevo_mante.write({
                    'etapa_id': etapa_programado.id,
                    'fecha_programado': fields.Date.today()
                })
                _logger.info("Mantenimiento creado de forma automática: ID %s", nuevo_mante.id)
                diccionario['mantenimiento_id'] = nuevo_mante.id
                nueva_cita = self.env['cita.mantenimiento'].create(diccionario)
                _logger.info("Nueva cita creada asociada al nuevo mantenimiento: ID %s", nueva_cita.id)
        else:
            _logger.warning(
                "No se localizó ningún vehículo con la matrícula '%s'. Creando cita sin vinculación de vehículo.",
                matricula)
            diccionario.update({
                'vehiculo_id': False,
                'mantenimiento_id': False,
                'cliente_id': False
            })
            nueva_cita = self.env['cita.mantenimiento'].create(diccionario)
            _logger.info("Cita sin vehículo creada exitosamente: ID %s", nueva_cita.id)
        _logger.info("== FIN process_cita para id_books: %s ==", id_books)

    def send_mail(self, res_id, email, name_template):
        _logger.info("Preparando envío de correo a %s usando template %s para res_id %s", email, name_template, res_id)
        odoo_bot = self.env['res.users'].sudo().browse(1)
        template = self.env.ref(name_template)
        template.with_user(odoo_bot).send_mail(
            res_id,
            force_send=True,
            email_values={
                'email_to': email
            }
        )
        _logger.info("Correo encolado / enviado exitosamente.")

    def update_cita(self, simply_id):
        _logger.info("Iniciando update_cita para simply_id: %s", simply_id)
        cita = self.search([('simplybook_id', '=', simply_id)])
        _logger.debug("Cita localizada en Odoo: %s", cita)
        etapa_reagenda = self.env['cita.mantenimiento.etapa'].search([('name', '=', 'Reagendada')], limit=1)
        data = False
        for i in range(3):
            _logger.debug("Intento %s para obtener individual_books", i + 1)
            data = self.individual_books(simply_id)
            if data:
                break
        if not data:
            _logger.error("No se pudo obtener datos tras 3 intentos en update_cita.")
            raise Exception("No se puedo obtener datos ")

        _logger.info("Actualizando datos de la cita en Odoo...")
        cita.write({
            'etapa_id': etapa_reagenda.id,
            'contador_reagenda': cita.contador_reagenda + 1,
            'fecha_cita_inicio': self._convertir_a_utc(data['start_date']),
            'fecha_cita_fin': self._convertir_a_utc(data['end_date']),
        })
        self.env.cr.commit()

        max_reagendas = int(self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.max_reagendas_au'))
        _logger.info("Contador reagenda au actual: %s, Máximo permitido: %s", cita.contador_reagenda_au, max_reagendas)

        if cita.contador_reagenda_au == max_reagendas:
            _logger.info("Límite de reagendas alcanzado. Enviando correo al cliente %s", self.cliente_id.email)
            email_to = self.cliente_id.email
            self.with_context(tz='America/Mexico_City').send_mail(cita.id, email_to,
                                                                  'cita_mantenimiento.cm_ultimo_cambio_mail_template')

    def actualizar_cita_simplyBook(self, fecha_inicio):
        _logger.info("Iniciando actualizar_cita_simplyBook. ID interno de cita: %s, Nueva fecha: %s", self.id,
                     fecha_inicio)
        try:
            url_update = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.book_details')
            if not url_update:
                raise Exception("Configuración faltante: url_update")
            url_construct = f"{url_update.rstrip('/')}/{int(self.simplybook_id)}"
            _logger.debug("URL para actualización: %s", url_construct)

            payload = ast.literal_eval(self.entity_raw)
            raw_data = payload.get('json_raw', {})
            dict_bookin = {
                "count": 1,
                "start_datetime": fecha_inicio,
                "provider_id": raw_data.get('provider_id'),
                "service_id": raw_data.get('service_id'),
                "client_id": raw_data.get('client_id'),
                "additional_fields": [{
                    'field': raw_data['additional_fields'][0]['field'] if raw_data.get('additional_fields') else None,
                    'value': raw_data['additional_fields'][0]['value'] if raw_data.get('additional_fields') else None,
                }, {
                    'field': raw_data['additional_fields'][1]['field'] if raw_data.get('additional_fields') else None,
                    'value': raw_data['additional_fields'][1]['value'] if raw_data.get('additional_fields') else None,
                }],
            }
            _logger.debug("Payload a enviar: %s", dict_bookin)

            respuesta = self.get_book_details(url_construct)
            time.sleep(0.5)

            if respuesta['status'] == 'canceled':
                _logger.info("La cita está cancelada en SimplyBook. Creando una nueva cita...")
                self.create_simplybook(mantenimiento_id=False, booking_dict=dict_bookin)
            else:
                _logger.info("Enviando petición PUT a SimplyBook para actualizar la cita...")
                response = self.helper_request("PUT", url_construct, json=dict_bookin)
                time.sleep(0.5)
                if response.status_code != 200:
                    error_msg = (
                        f"Error al actualizar en SimplyBook.\n"
                        f"Status: {response.status_code}\n"
                        f"Body: {response.text}"
                    )
                    _logger.error(error_msg)
                    raise Exception(error_msg)
                _logger.info("Cita actualizada exitosamente en SimplyBook.")
        except Exception as e:
            _logger.exception("Excepción inesperada al actualizar cita en SimplyBook: %s", str(e))
            raise

    def check_proveedor_valido(self, provider_id, vehiculo_plaza, vehiculo, odometro):
        _logger.info(f"Entrando a validación de proveedor:  {vehiculo}")
        provedor_odoo = self.env['res.partner'].search([('simplybook_proveedor_id', '=', provider_id)], limit=1)
        if not provedor_odoo:
            url_base = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.provider_list')
            url_individual = f"{url_base.rstrip('/')}/{int(provider_id)}"
            proveedor_data = self.get_book_details(url_individual)
            if proveedor_data and proveedor_data.get('phone'):
                phone_id = int(proveedor_data['phone'].replace("+52", ""))
                provedor_odoo = self.env['res.partner'].search([('id', '=', phone_id),('es_proveedor', '=', True)], limit=1)
                if provedor_odoo:
                    provedor_odoo.sudo().write({'simplybook_proveedor_id': provider_id})
        if provedor_odoo:
            existe = self.env['cm.proveedor.plaza'].search([('plaza_id', '=', vehiculo_plaza),('provedoor_ids', 'in', [provedor_odoo.id])], limit=1)
            if existe:
                talleres_au = self.env['cm.taller.autorizado'].search([('brand_id', '=', vehiculo.brand_id.id),('plaza_id','=', vehiculo_plaza)], limit=1)
                _logger.info(f"Entra a existe y de valida talleres_au")
                if talleres_au:
                    _logger.info("Exisye talleres_au")
                    _logger.info(f"Taller odoo:  {provedor_odoo}")
                    _logger.info(f"Talleres por marca:  {talleres_au.taller_autorizado_ids}")
                    _logger.info(f"Maximo km permitido: {talleres_au.km_permitido}")
                    proveedor_autorizado = provedor_odoo.id in talleres_au.taller_autorizado_ids.ids
                    _logger.info(f"proveedor_autorizado: {proveedor_autorizado}")
                    if not proveedor_autorizado and odometro < talleres_au.km_permitido:
                        return {
                            "errors": [
                                f"Las unidades {vehiculo.brand_id.name} menores a "
                                f"{talleres_au.km_permitido:,} km solo pueden ser atendidas "
                                "en talleres autorizados."
                            ]
                        }
                    if proveedor_autorizado and odometro > talleres_au.km_permitido:
                        return {
                            "errors": [
                                f"Las unidades {vehiculo.brand_id.name} mayores a "
                                f"{talleres_au.km_permitido:,} km deben ser atendidas "
                                "en talleres genericos"
                            ]
                        }
                else:
                    existe_taller = self.env['cm.taller.autorizado'].search([('taller_autorizado_ids','in', [provedor_odoo.id])], limit=1)
                    if existe_taller:
                        return {
                            "errors": [
                                f"El taller seleccinado solo acepta vehiculos de la marca {existe_taller.brand_id.name}. "
                            ]
                        }
                return {}
            else:
                return {
                    "errors": [self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.msg_placa_otra_plaza')]
                }
        return {
            "errors": ["El proovedor no existe en el sistema base"]
        }

    def cancel_cita_simply(self, simplybook_id):
        _logger.info("Iniciando cancelación en SimplyBook para ID %s", simplybook_id)
        url_delete = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.admin')
        url_construct = f"{url_delete.rstrip('/')}/{simplybook_id}"
        _logger.debug("Enviando petición DELETE a %s", url_construct)
        response = self.helper_request("DELETE", url_construct)
        if response.status_code != 200:
            error_details = (
                f"Error SimplyBook:\n"
                f"Status: {response.status_code}\n"
                f"Headers: {response.headers}\n"
                f"Body: {response.text}"
            )
            _logger.error("Error al cancelar cita en SimplyBook: %s", error_details)
            raise Exception(error_details)
        if response.ok:
            _logger.info("Cita cancelada exitosamente en SimplyBook.")
            return response.json()
        else:
            return None

    def cancel_cita(self, id_books):
        _logger.info("Cancelando cita internamente en Odoo para simplybook_id: %s", id_books)
        etapa_cancelada = self.env['cita.mantenimiento.etapa'].search([('name', '=', 'Cancelada')])
        cita = self.search([('simplybook_id', '=', id_books)], limit=1)
        if cita:
            cita.etapa_id = etapa_cancelada.id
            _logger.info("Cita en Odoo (ID: %s) marcada como Cancelada.", cita.id)
        else:
            _logger.warning("No se encontró cita en Odoo para cancelar con simplybook_id: %s", id_books)

    def ultimo_slot(self, fecha, service_id, provider_id):
        _logger.info("Consultando último slot disponible para la fecha %s, servicio %s, proveedor %s", fecha,
                     service_id, provider_id)
        url_consulta = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.first_available_slot')
        params = {
            'service_id': service_id,
            'provider_id': provider_id,
            'date': str(fecha.date()),
        }
        try:
            response = self.helper_request("GET", url_consulta, params=params)
            json_dict = response.json()
            fecha_inicio = json_dict['id']
            fecha_fin = datetime.strptime(fecha_inicio, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
            _logger.info("Slot encontrado: %s a %s", fecha_inicio, fecha_fin)
            return {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
            }
        except Exception as e:
            _logger.error(f"❌ Error al obtener último slot: {str(e)}", exc_info=True)
            return None

    def crear_peticion_bloqueo(self):
        _logger.info("Iniciando creación de petición de bloqueo...")
        for record in self:
            _logger.info("Procesando bloqueo para registro ID: %s, Vehículo ID: %s", record.id, record.vehiculo_id.id)
            contrato = self.env['fleet.vehicle.log.contract'].search([('vehicle_id', '=', record.vehiculo_id.id)],
                                                                     limit=1)
            operacion = self.env['agenda.peticion.bloqueo.tipo'].search([('name', '=', 'Bloquear')], limit=1)
            peticion = self.env['fleet.tecno.peticion.bloqueo'].create_custom({
                'tipoOperacion': operacion.id,
                'numeroContrato': contrato.ins_ref,
                'codigoAreaSolicitante': False,
                'idUsuario': self.env.user.id,
                'motivoSolicitud': "Incumplimiento de mantenimiento",
                'fechaHoraRequerimiento': str(fields.Datetime.now()),
                'codigoRespuesta': 1,
            })
            _logger.info("Petición de bloqueo creada exitosamente.")

    def return_km_add(self,fecha_planeada,ahora_local):
        km_promedio_dia = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.km_promedio')
        diferencia = fecha_planeada - ahora_local
        segundos = diferencia.total_seconds()
        dias = segundos / 86400
        km_add = dias * int(km_promedio_dia)
        return int(km_add)

    def validar_cita(self, data):
        saltar_validacion = False
        etapa_requerido = self.return_etapa_mante('Requerido')
        etapa_programado = self.return_etapa_mante('Programado')
        etapa_proceso = self.return_etapa_mante('En proceso')
        etapa_realizado = self.return_etapa_mante('Realizado')
        etapa_finalizado = self.return_etapa_mante('Finalizado')
        tipo_mantenimiento = self.return_tipo_mante('Vehicular Preventivo')
        matricula = data['additional_fields'][0]['value']
        matricula = matricula.upper()
        llave = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.llave_creacion')
        if llave in matricula:
            matricula = matricula.replace("-MTTO","")
            saltar_validacion = True
        odometro_simply = data['additional_fields'][1]['value']
        vehiculo = self.env['fleet.vehicle'].search([('license_plate', '=', matricula)], limit=1)
        fecha_planeada = self._convertir_a_utc(data.get('start_datetime'))
        ahora_local = fields.Datetime.now()
        km_add = self.return_km_add(fecha_planeada, ahora_local)
        odometro_actual = int(odometro_simply) + km_add
        limite_inferior = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.limite_inferior')
        limite_superior  = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.limite_superior')
        if vehiculo:
            if saltar_validacion:
                return {}
            ultimo_mantenimiento = self.env['fleet.mantenimiento'].search([('vehiculo_id', '=', vehiculo.id),('tipo_mantenimiento_id', '=',tipo_mantenimiento.id),
                                                                           ('etapa_id', 'in',[etapa_realizado.id, etapa_finalizado.id])],limit=1, order='id desc')
            if ultimo_mantenimiento:
                km_prox_mantenimiento = ultimo_mantenimiento.km_entrada + 10000
                _logger.info("==================Validación SB================")
                _logger.info(f"KM_prox:{km_prox_mantenimiento}")
                _logger.info(f"KM añadidos :{km_add}")
                km_prox_inferior = km_prox_mantenimiento - int(limite_inferior)
                _logger.info(f"KM proximos inferior :{km_prox_inferior}")
                km_prox_superior = km_prox_mantenimiento + int(limite_superior)
                _logger.info(f"KM proximos superior:{km_prox_superior}")
                _logger.info(f"KM in de odometro :{km_prox_inferior}")
                _logger.info(f"Odometro_actual:{odometro_actual}")
                if odometro_actual < km_prox_inferior:
                    return {
                        "errors": [
                            self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.msg_rango_minimo')
                        ]
                    }
                if odometro_actual > km_prox_superior:
                    return {
                        "errors": [
                             self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.msg_rango_maximo')
                        ]
                    }
            else:
                km_prox_inferior = 10000 - int(limite_inferior)
                km_prox_superior = 10000 + int(limite_superior)
                if odometro_actual > km_prox_superior:
                    return {
                        "errors": [
                            self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.msg_desfase_mantenimientos')
                        ]
                    }
                if not (km_prox_inferior <= odometro_actual <= km_prox_superior):
                    return {
                        "errors": [
                             self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.msg_primer_mantenimiento')
                        ]
                    }
            mantenimiento = self.env['fleet.mantenimiento'].search([('vehiculo_id', '=', vehiculo.id),
                                                                    ('etapa_id', 'in', [etapa_requerido.id, etapa_programado.id, etapa_proceso.id]),
                                                                    ('tipo_mantenimiento_id', '=', tipo_mantenimiento.id)], limit=1)
            if mantenimiento:
                cita_vinculada = self.search([('mantenimiento_id', '=', mantenimiento.id)], limit=1)
                max_reagendas = int(
                    self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.max_reagendas'))
                if cita_vinculada:
                    if cita_vinculada.reagenda_automatica:
                        return {}
                    else:
                        if cita_vinculada.contador_reagenda >= max_reagendas:
                            return {
                                "errors": [
                                    self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.msg_max_reagendas')
                                ]
                            }
                        else:
                            max_reagendas_au = int(self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.max_reagendas_au'))
                            if cita_vinculada.contador_reagenda_au >= max_reagendas_au:
                                return {
                                    "errors": [f"Ya haz actualizado {max_reagendas_au} veces tu agenda manualmente."]
                                }
                            else:
                                return self.check_proveedor_valido(int(data['provider_id']), vehiculo.plaza_id.id, vehiculo, odometro_actual)
                else:
                    return self.check_proveedor_valido(int(data['provider_id']), vehiculo.plaza_id.id, vehiculo, odometro_actual)
            else:
                return self.check_proveedor_valido(int(data['provider_id']), vehiculo.plaza_id.id, vehiculo, odometro_actual)
        else:
            return {
                'additional_fields': [{
                    'id': 'f589749c18669980e67d41355c039b30',
                    'errors': [
                        self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.msg_placa_no_encontrada')]
                }]
            }

    def get_list_simply_client(self, params):
        _logger.debug("Obteniendo lista de clientes de SimplyBook con parámetros: %s", params)
        url_cliente_list = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.admin_clients')
        response = self.helper_request("GET", url_cliente_list, params=params)
        response = response.json()
        return response

    def lista_cliente_simply(self):
        _logger.info("Descargando la lista completa de clientes desde SimplyBook...")
        params = {
            'page': 1,
            'on_page': 100
        }
        data = self.get_list_simply_client(params)
        total_pages = data['metadata']['pages_count']
        all_data_clients = data['data']
        _logger.debug("Página 1 procesada. Total de páginas a procesar: %s", total_pages)

        for page in range(2, total_pages + 1):
            _logger.debug("Procesando página de clientes: %s", page)
            params['page'] = page
            data = self.get_list_simply_client(params)
            all_data_clients += data['data']

        _logger.info("Total de clientes obtenidos: %s", len(all_data_clients))
        return all_data_clients

    def crear_cliente_simply(self, cliente_id):
        _logger.info("Iniciando creación/mapeo de cliente SimplyBook para el cliente de Odoo ID: %s", cliente_id)
        cliente = self.env['res.partner'].search([('id', '=', cliente_id)], limit=1)
        if not cliente.simplybook_cliente_id:
            _logger.info("Cliente %s no tiene ID de SimplyBook. Buscando en la lista existente...", cliente.name)
            data = self.lista_cliente_simply()
            map_users = {
                c['email']: c for c in data
            }
            cliente_existente = map_users.get(cliente.email)
            if cliente_existente:
                _logger.info("Cliente encontrado en SimplyBook por email. Vinculando ID %s", cliente_existente['id'])
                cliente.simplybook_cliente_id = cliente_existente['id']
                return cliente_existente['id']
            else:
                _logger.info("El cliente no existe en SimplyBook. Procediendo a crear...")
                url_cliente = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.admin_clients')
                json_data = {
                    "name": cliente.display_name,
                    "email": cliente.email,
                    "phone": cliente.phone,
                }
                response = self.helper_request("POST", url_cliente, json=json_data)
                nuevo_cliente = response.json()
                cliente.simplybook_cliente_id = nuevo_cliente['id']
                _logger.info("Cliente creado en SimplyBook con ID %s", nuevo_cliente['id'])
                return nuevo_cliente['id']
        else:
            _logger.info("Cliente Odoo ya tiene vinculado su simplybook_cliente_id: %s", cliente.simplybook_cliente_id)
            return cliente.simplybook_cliente_id

    def validar_proveedor_simply(self, plaza_id):
        _logger.info("Validando proveedor SimplyBook para la plaza ID: %s", plaza_id)
        proveedores_plaza = self.env['cm.proveedor.plaza'].search([('plaza_id', '=', plaza_id)])
        proveedor_id = random.choice(proveedores_plaza.provedoor_ids.ids)
        _logger.debug("Proveedor elegido aleatoriamente: ID %s", proveedor_id)
        proveedor_odoo = self.env['res.partner'].browse(proveedor_id)

        if proveedor_odoo.simplybook_proveedor_id:
            _logger.info("Proveedor Odoo ya tiene ID vinculado: %s", proveedor_odoo.simplybook_proveedor_id)
            return proveedor_odoo.simplybook_proveedor_id
        else:
            _logger.info("Proveedor Odoo no tiene ID vinculado. Buscando coincidencias por teléfono...")
            providers_list = self.provider_list()
            provider_map = {
                int(phone.replace("+52", "")): p
                for p in providers_list['data']
                if (phone := p.get('phone'))
            }
            proveedor_simply = provider_map.get(proveedor_id)
            if proveedor_simply:
                proveedor_odoo.simplybook_proveedor_id = proveedor_simply['id']
                _logger.info("Proveedor vinculado exitosamente con SimplyBook ID: %s", proveedor_simply['id'])
                return proveedor_simply['id']
            else:
                _logger.error("No se pudo mapear el proveedor en la lista devuelta por SimplyBook.")
                return False

    def fecha_formato(self, fecha):
        _logger.debug("Convirtiendo fecha UTC a zona local México: %s", fecha)
        zona_local = pytz.timezone('America/Mexico_City')
        fecha_utc = pytz.utc.localize(fecha)
        fecha_real = fecha_utc.astimezone(zona_local)
        _logger.debug("Fecha convertida: %s", fecha_real)
        return fecha_real

    def create_simplybook(self, mantenimiento_id, booking_dict):
        _logger.info("=== INICIANDO CREATE SIMPLYBOOK ===")
        url = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.admin')
        if booking_dict:
            _logger.info("Se recibió un booking_dict predefinido. Realizando POST...")
            _logger.debug("Payload: %s", booking_dict)
            response = self.helper_request("POST", url, json=booking_dict)
            time.sleep(0.5)
        else:
            _logger.info("Generando booking_dict desde mantenimiento_id: %s", mantenimiento_id)
            mantenimiento = self.env['fleet.mantenimiento'].browse(mantenimiento_id)
            cliente_simply = self.crear_cliente_simply(mantenimiento.conductor_id.id)
            provedoor_simply = self.validar_proveedor_simply(mantenimiento.plaza_id.id)
            nueva_fecha_base = mantenimiento.create_date + timedelta(days=2)
            fechas = self.ultimo_slot(nueva_fecha_base, 4, provedoor_simply)

            dict_bookin = {
                "count": 1,
                "start_datetime": fechas.get('fecha_inicio'),
                "provider_id": provedoor_simply,
                "service_id": 4,
                "client_id": cliente_simply,
                "additional_fields": [{
                    'field': "f589749c18669980e67d41355c039b30",
                    'value': mantenimiento.vehiculo_id.license_plate,
                }, {
                    'field': "7ff61a241dc228b868f8f1165869516c",
                    'value': int(mantenimiento.vehiculo_id.odometro_mod),
                }],
            }
            _logger.debug("Payload dinámico construido: %s", dict_bookin)
            try:
                response = self.helper_request("POST", url, json=dict_bookin)
                time.sleep(0.5)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                if hasattr(e.response, 'text'):
                    _logger.error("Respuesta del error al crear SimplyBook: %s", e.response.text)
                return False

        if response.status_code in [200, 201]:
            _logger.info("✅ Cita creada exitosamente en SimplyBook. Status: %s", response.status_code)
            _logger.debug("Respuesta del servidor: %s", response.text)
        else:
            _logger.warning("⚠️ SimplyBook devolvió un código inesperado: %s", response.status_code)
            _logger.warning("Contenido de la respuesta: %s", response.text)
        _logger.info("🏁 ===== FIN CREATE SIMPLYBOOK =====")
        return response

    def reagendar_cita(self):
        _logger.info("Iniciando proceso por lote de reagendar_cita...")
        etapa_programada = self.env['cita.mantenimiento.etapa'].search([('name', '=', 'Programada')], limit=1)
        etapa_reagenda = self.env['cita.mantenimiento.etapa'].search([('name', '=', 'Reagendada')], limit=1)
        citas = self.search([('etapa_id', 'in', [etapa_programada.id, etapa_reagenda.id])])
        _logger.info("Se encontraron %s citas para evaluar reagenda.", len(citas))
        max_reagendas_param_au = self.env['ir.config_parameter'].sudo().get_param('cita_mantenimiento.max_reagendas_au')
        max_reagendas_au = int(max_reagendas_param_au or 0)
        for record in citas:
            try:
                _logger.debug("Evaluando cita ID: %s, contador reagenda au: %s", record.id, record.contador_reagenda_au)
                if record.contador_reagenda_au < max_reagendas_au:
                    fecha_prevista_reagenda = record.fecha_cita_inicio + timedelta(days=1)
                    fecha_local = self.convertir_a_hora_local(fecha_prevista_reagenda)
                    ahora_local = self.convertir_a_hora_local(fields.Datetime.now())
                    if fecha_local <= ahora_local:
                        _logger.info("Es momento de reagendar la cita ID %s. Procesando...", record.id)
                        payload = ast.literal_eval(record.entity_raw)
                        service_id = payload['json_raw']['service_id'] if payload['json_raw']['service_id'] else None
                        provider_id = payload['json_raw']['provider_id'] if payload['json_raw']['provider_id'] else None
                        nueva_fecha_base = fecha_local + timedelta(days=2)
                        fechas = self.ultimo_slot(nueva_fecha_base, service_id, provider_id)
                        time.sleep(0.5)

                        _logger.debug("Marcando cita %s con reagenda automática...", record.id)
                        record.write({
                            'reagenda_automatica': True,
                            'contador_reagenda_au': record.contador_reagenda_au + 1
                        })
                        self.env.cr.commit()
                        record.actualizar_cita_simplyBook(fechas['fecha_inicio'])
                        _logger.info("Cita ID %s reagendada automáticamente con éxito.", record.id)
                    else:
                        _logger.info("⏱️ Aún no es momento de reagendar para la cita ID: %s", record.id)
                else:
                    _logger.info("🚫 Cita ID %s no cumple condición de máximo de reagendas (%s >= %s)", record.id,
                                 record.contador_reagenda_au, max_reagendas_au)
            except Exception as e:
                _logger.error(f"❌ Error al procesar cita ID {record.id}: {str(e)}", exc_info=True)

        _logger.info("Reestableciendo el flag 'reagenda_automatica' para todas las citas procesadas.")
        citas.write({
            'reagenda_automatica': False
        })
        _logger.info("Proceso de reagendar_cita finalizado.")