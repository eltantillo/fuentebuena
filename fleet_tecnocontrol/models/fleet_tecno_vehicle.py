import requests
from odoo import fields, api, models
import json
import urllib.request
import urllib.error
import logging
import re

_logger = logging.getLogger(__name__)

class FleetTecnoVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    id_gps = fields.Char(
        string="Id GPS",
    )
    estado_bloqueo_id = fields.Many2one(
        string="Estado Bloqueo",
        comodel_name="tecno.peticion.estado",
        domain="['|',('name', '=', 'Bloqueado'),('name', '=', 'Desbloqueado')]",
        tracking=True
    )
    ubicacion = fields.Char(
        string="Última ubicación",
    )
    external_gps_provider = fields.Selection(
        selection_add=[
            ('tecnocontrol', 'Tecnocontrol'),
        ]
    )

    def asignar_gps(self):
        _logger.info("Iniciando asignación de GPS desde Tecnocontrol.")
        vehiculos = self.search([])
        vehiculos_map = {v.vin_sn: v for v in vehiculos}
        url = (self.env["ir.config_parameter"].sudo().get_param("fleet_tecnocontrol.url_private_units"))
        tcv_client = (self.env["ir.config_parameter"].sudo().get_param("fleet_tecnocontrol.tcv_client_id"))
        headers = {
            "Content-Type": "application/json",
            "Tcv-Client-ID": tcv_client,
        }
        try:
            response = requests.request("GET", url, headers=headers)
            response.raise_for_status()
            vehiculos_json = response.json()
        except Exception as e:
            _logger.error("Error al consultar la API de Tecnocontrol: %s", str(e))
            return
        for vehiculo in vehiculos_json:
            vin = vehiculo.get("serie")
            id_gps = vehiculo.get("idgps")
            fleet = vehiculos_map.get(vin)
            if fleet:
                fleet.write(
                    {
                        "id_gps": id_gps,
                        "external_gps_id": id_gps,
                        "external_gps_provider": "tecnocontrol",
                    }
                )
            else:
                _logger.info(
                    "VIN %s no encontrado en flotas. Registrando en 'fleet.tecno.no.gps' (GPS: %s).",
                    vin,
                    id_gps,
                )
                no_gps = self.env["fleet.tecno.no.gps"].search(
                    [("id_gps", "=", id_gps)], limit=1
                )
                if no_gps:
                    no_gps.write({"vin_sn": vin})
                else:
                    self.env["fleet.tecno.no.gps"].create(
                        {"id_gps": id_gps, "vin_sn": vin}
                    )
        _logger.info(
            "Proceso de asignación de GPS finalizado. Total procesados: %s",
            len(vehiculos),
        )

    def return_equivalencia(self,field):
        maping = {
            "Desactivado": "Desbloqueado",
            "Activado": "Bloqueado",
        }
        return  maping.get(field,field)

    def consultar_vehiculo(self, tipo_peticion):
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_tecnocontrol.url_reporte_bloqueos')
        tcv_client = self.env['ir.config_parameter'].sudo().get_param('fleet_tecnocontrol.tcv_client_id')
        headers = {
            'Content-Type': 'application/json',
            'Tcv-Client-ID': tcv_client,
        }
        params = [{
            "PETICION": tipo_peticion
        }]
        response = requests.post(url, json=params, headers=headers)
        if response:
            data = response.json()
            return data
        else:
            return False

    def process_ubicacion(self, ubicacion):
        if not ubicacion:
            return False
        else:
            match = re.search(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)', ubicacion)
            if match:
                return f"{match.group(1)},{match.group(2)}"
            return None

    def asignar_estado_bloqueo(self):
        odometros = self.consultar_vehiculo(0)
        if not odometros:
            return
        pendiente_peticion = self.env['tecno.peticion.estado'].search(
            [('name', '=', 'Pendiente')], limit=1
        )
        for record in odometros:
            vin = record.get('SERIE')
            if not vin:
                continue
            vin_clean = str(vin).strip()
            vehiculo = self.search([('vin_sn', '=', vin_clean)], limit=1)
            if not vehiculo:
                continue
            bloqueo_raw = record.get('BLOQUEO_DE_MOTOR')
            if bloqueo_raw:
                equivalencia = self.return_equivalencia(str(bloqueo_raw).strip())
                estado = self.env['tecno.peticion.estado'].search(
                    [('name', '=', equivalencia)], limit=1
                )
                if estado and vehiculo.estado_bloqueo_id != estado:
                    vehiculo.estado_bloqueo_id = estado.id
                    if pendiente_peticion:
                        peticion = self.env[
                            'fleet.tecno.peticion.bloqueo'
                        ].search(
                            [
                                ('vehiculo_contrato_id', '=', vehiculo.id),
                                ('estado_id', '=', pendiente_peticion.id),
                            ],
                            limit=1,
                        )
                        if peticion:
                            peticion.estado_id = estado.id
            ubicacion_raw = record.get('UBICACION')
            if ubicacion_raw:
                vehiculo.ubicacion = self.process_ubicacion(ubicacion_raw)