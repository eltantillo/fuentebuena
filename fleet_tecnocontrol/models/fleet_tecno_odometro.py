import requests
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class FleetTecnoOdometro(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    @api.model
    def create_custom(self, vals_list):
        if not vals_list:
            return False
        return super(FleetTecnoOdometro, self).create(vals_list)

    def limpiar_valor(self, valor):
        if valor:
            odometro_kms = (
                valor
                .replace(" Km", "")
                .replace(",", "")
                .strip()
            )
            return float(odometro_kms)
        else:
            return False

    def consultar_vehiculo(self, tipo_peticion):
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_tecnocontrol.url_reporte_bloqueos')
        tcv_client = self.env['ir.config_parameter'].sudo().get_param(
            'fleet_tecnocontrol.tcv_client_id'
        )
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

    def buscar_vehiculo(self):
        vehiculos = self.env['fleet.vehicle'].search([
            ('producto_id', 'in', [1, 6, 7, 8])
        ])
        _logger.info("Datos del los vehiculos dentro de busca")
        _logger.info(len(vehiculos))
        return vehiculos

    def mapeo_vehiculos(self):
        odometros_globales = self.consultar_vehiculo(0)
        # odometro_desbloqueado = self.consultar_vehiculo(1)
        # odometro_bloqueado = self.consultar_vehiculo(2)
        # if odometro_desbloqueado and odometro_bloqueado:
        if odometros_globales:
            # odometros = odometro_bloqueado + odometro_desbloqueado
            odometros = odometros_globales
            odometros_map = {
                o["SERIE"]: o["ODO_KMS"] for o in odometros if o.get("SERIE")
            }
            odometros_mod_map = {
                o['SERIE']: o['ODOMETRO_APLICADO'] for o in odometros if o.get('FECHA_APLICACION')
            }
            _logger.info(odometros_mod_map)
            return odometros_map, odometros_mod_map
        else:
            return False

    def assign_odometro_create(self):
        vehiculos = self.buscar_vehiculo()
        odometros_map, odometros_mod_map = self.mapeo_vehiculos()
        if odometros_map:
            chunk_size = 100
            for i in range(0, len(vehiculos), chunk_size):
                lote = vehiculos[i:i + chunk_size]
                vals_list = []
                for vehiculo in lote:
                    odometro = odometros_map.get(vehiculo.vin_sn)
                    odometro_limpio = self.limpiar_valor(odometro)
                    if odometro_limpio:
                        vehiculo.odometro_mod = odometro_limpio
                        vals_list.append({
                            'vehicle_id': vehiculo.id,
                            'value': odometro_limpio,
                        })
                if vals_list:
                    self.env['fleet.vehicle.odometer'].create_custom(vals_list)
                    self.env.cr.commit()
                else:
                    continue

    def assign_odometro_write(self):
        vehiculos = self.buscar_vehiculo()
        etapa_registrado = self.env['actualizar.odometro.etapa'].search([('name', '=', 'Registrado')])
        etapa_aplicado = self.env['actualizar.odometro.etapa'].search([('name', '=', 'Aplicado')])
        peticiones_odometro = self.env['fleet.tecno.actualizar.odometro'].search([('etapa_id', '=', etapa_registrado.id)])
        odometros_map, odometros_mod_map = self.mapeo_vehiculos()
        if odometros_map:
            chunk_size = 100
            for i in range(0, len(vehiculos), chunk_size):
                lote = vehiculos[i:i + chunk_size]
                for vehiculo in lote:
                    peticiones = peticiones_odometro.filtered(lambda x: x.vin == vehiculo.vin_sn)
                    odometro_aplicado = odometros_mod_map.get(vehiculo.vin_sn)
                    if peticiones and odometro_aplicado is not None:
                        for peticion in peticiones:
                            if float(peticion.odometro) == float(odometro_aplicado):
                                peticion.write({
                                    'etapa_id': etapa_aplicado.id,
                                })
                    odometro = odometros_map.get(vehiculo.vin_sn)
                    odometro_limpio = self.limpiar_valor(odometro)
                    if odometro_limpio:
                        ultimo = self.env['fleet.vehicle.odometer'].search([
                            ('vehicle_id', '=', vehiculo.id)
                        ], limit=1, order='date desc')
                        if ultimo:
                            vehiculo.odometro_mod = odometro_limpio
                            ultimo.write({
                                'value': odometro_limpio
                            })
                        else:
                            continue
                    else:
                        continue