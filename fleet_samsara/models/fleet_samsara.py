import json

import requests
from odoo import fields,models,api
import logging

_logger = logging.getLogger(__name__)

class FleetSamsara(models.Model):
    _name = 'fleet.samsara'

    def _llamada_samsara(self, method, url, params, json=None):
        url = url
        token = self.env['ir.config_parameter'].sudo().get_param('fleet_samsara.token')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        response = requests.request(method, url, headers=headers, params=params, json=json)
        return response

    def obtener_informacion_vehicle(self, url, params):
        url = url
        after = None
        data = []
        _logger.info("Proceso desde obtener inforación vehicle")
        _logger.info(params)
        while True:
            if after:
                params["after"] = after
            response = self._llamada_samsara("GET",url, params=params)
            response = response.json()
            data.extend(response.get("data", []))
            pagination = response.get("pagination", {})
            if not pagination.get("hasNextPage"):
                break
            after = pagination.get("endCursor")
        return data

    def vincular_gps_vehicle(self):
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_samsara.vehicles')
        data = self.obtener_informacion_vehicle(url, {},)
        vehiculos = self.env['fleet.vehicle'].search([])
        vehiculo_map = {v.vin_sn: v for v in vehiculos}
        for record in data:
            if 'vin' in record:
                vin = record['vin']
                id_samsara = record['id']
                vehiculo = vehiculo_map.get(vin)
                if vehiculo:
                    vehiculo.external_gps_id = id_samsara
                    vehiculo.external_gps_provider = 'samsara'

    def ultima_ubicacion_vehicle(self):
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_samsara.locations')
        data = self.obtener_informacion_vehicle(url, {})
        vehiculos = self.env['fleet.vehicle'].search([('external_gps_provider','=','samsara')])
        vehiculo_map = {v.external_gps_id: v for v in vehiculos}
        for record in data:
            if any(key in record for key in ('id', 'location')):
                vehiculo = vehiculo_map.get(record['id'])
                if vehiculo:
                    vehiculo.external_longitud = str(record['location']['longitude'])
                    vehiculo.external_latitud = str(record['location']['latitude'])

    def datos_odometro(self):
        vehicles_samsara = self.env['fleet.vehicle'].search([('external_gps_provider', '=', 'samsara')])
        vehicles_samsara_map = {
            v.external_gps_id: v for v in vehicles_samsara
        }
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_samsara.stats')
        params = {'types': 'obdOdometerMeters'}
        data = self.obtener_informacion_vehicle(url, params)
        data_samsara = []
        for record in data:
            if 'id' in record:
                odometro_metros = float(record['obdOdometerMeters']['value']) if record['obdOdometerMeters'] else 0.0
                data_samsara.append({
                    "id": record['id'],
                    "odometro_metros": odometro_metros/1000
                })
        return  vehicles_samsara_map, data_samsara


    def create_odometer(self):
        samsara_map, data_samsara = self.datos_odometro()
        for record in data_samsara:
            vehiculo = samsara_map.get(record['id'])
            if vehiculo:
                self.env['fleet.vehicle.odometer'].create({
                    'vehicle_id': vehiculo.id,
                    'value': record['odometro_metros'],
                })

    def update_odometer(self):
        samsara_map, data_samsara = self.datos_odometro()
        vehicle_ids = [v.id for v in samsara_map.values()]
        query = """
                SELECT DISTINCT ON (vehicle_id) id, vehicle_id
                FROM fleet_vehicle_odometer
                WHERE vehicle_id IN %s
                ORDER BY vehicle_id, date DESC, id DESC
        """
        self.env.cr.execute(query, (tuple(vehicle_ids),))
        results = self.env.cr.dictfetchall()
        _logger.info("=======================0")
        _logger.info(results)

    def _llamada_bloqueo(self, samsara_id, state):
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_samsara.vehicles')
        url = url.replace('.com/', '.com/beta/')
        if samsara_id:
            new_url = url + f"/{samsara_id}/immobilizer"
            _logger.info(new_url)
            json = {
                "relayStates": [
                    {
                        "id": "relay1",
                        "isOpen": state
                    }
                ]
            }
            estado_p = False
            response = self._llamada_samsara("PATCH", new_url,{}, json)
            if response.status_code == 202:
                estado_p = True
                return "Petición registrada exitosamente",estado_p
            elif response.status_code == 400:
                response = response.json()
                mensaje = response['message']
                return mensaje, estado_p
            else:
                return "Error al registrar",estado_p

    def block_vehicle(self, samsara_id):
        msg,estado = self._llamada_bloqueo(samsara_id, True)
        return msg,estado

    def unblock_vehicle(self, samsara_id):
        msg,estado = self._llamada_bloqueo(samsara_id, False)
        return msg,estado
