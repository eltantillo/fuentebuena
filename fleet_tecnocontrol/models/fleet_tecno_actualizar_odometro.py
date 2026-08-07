"""
@author: Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>
@date: 29/05/2025
"""

import json
import urllib.request
import urllib.error
from odoo import fields,models,api
from odoo.exceptions import UserError, ValidationError

class ActualizarOdometro(models.Model):
    _name = 'fleet.tecno.actualizar.odometro'
    _description = 'Actualizar odometro'

    vehicle_id = fields.Many2one(
        comodel_name = 'fleet.vehicle',
        string = 'Vehículo',
    )
    cliente = fields.Char(
        string = 'Cliente',
        compute='_compute_cliente',
        store=True,
    )
    vin = fields.Char(
        string = 'VIN',
        compute='_compute_vin',
        store=True,
    )
    odometro = fields.Float(
        string = 'Odómetro',
        required=True,
    )
    mensaje = fields.Char(
        string = 'Mensaje',
    )
    codigo = fields.Char(
        string = 'Código',
    )
    etapa_id = fields.Many2one(
        comodel_name = 'actualizar.odometro.etapa',
        string = 'Etapa',
    )

    @api.constrains('odometro')
    def _check_odometro(self):
        for rec in self:
            if rec.odometro <= 0:
                raise ValidationError("El odómetro debe ser mayor a 0.")

    def process_peticion_odometro(self):
        etapa_reg = self.env['actualizar.odometro.etapa'].search([('name', '=', 'Registrado')])

    @api.depends('vehicle_id')
    def _compute_vin(self):
        for odometro in self:
            odometro.vin = odometro.vehicle_id.vin_sn

    @api.depends('vehicle_id')
    def _compute_cliente(self):
        for odometro in self:
            odometro.cliente = odometro.vehicle_id.driver_id.name

    @api.model
    def create(self, vals_list):
        registro = super().create(vals_list)
        registro.send_data()
        return registro

    def send_data(self):
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_tecnocontrol.comandoOdometro')
        data = json.dumps([{
            "ESN": self.vin,
            "ODOMETRO": int(self.odometro * 1000),
        }]).encode('utf-8')
        tcv_client = self.env['ir.config_parameter'].sudo().get_param('fleet_tecnocontrol.tcv_client_id')
        headers = {
            'Content-Type': 'application/json',
            'Tcv-Client-ID': tcv_client,
        }
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                data_respuesta = res.read().decode('utf-8')
                respuesta_json = json.loads(data_respuesta)
                self.write({'mensaje': respuesta_json[0].get('MENSAJE'),
                            'codigo': respuesta_json[0].get('CODIGO'),})
        except urllib.error.HTTPError as e:
            raise UserError(f"Error HTTP: {e.code}")
        except urllib.error.URLError as e:
            raise UserError(f"No se pudo conectar: {e.reason}")
        return True