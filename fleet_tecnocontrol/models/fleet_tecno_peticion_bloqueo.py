from odoo import fields,api,models
from datetime import datetime
import requests

import logging
_logger = logging.getLogger(__name__)

class FleetTecnoPeticionBloqueo(models.Model):
    _name = 'fleet.tecno.peticion.bloqueo'
    _rec_name = 'rec_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    estado_id = fields.Many2one(
        comodel_name='tecno.peticion.estado',
        string="Etapa",
        tracking=True
    )
    tipo_operacion = fields.Many2one(
        comodel_name='agenda.peticion.bloqueo.tipo',
        string="Tipo de operacion",
    )
    numero_contrato = fields.Char(
        string="Numero de contrato",
    )
    vehiculo_contrato_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string="Vehiculo de contrato",
    )
    vin_sn = fields.Char(
        string="VIN",
    )
    cod_area_solicitante = fields.Char(
        string="Cod de area solicitante",
    )
    id_usuario = fields.Char(
        string="ID de usuario",
    )
    motivo_solicitud = fields.Char(
        string="Motivo de solicitud",
    )
    fecha_hora_req = fields.Datetime(
        string="Fecha de hora de request",
    )
    rec_name = fields.Char(
        string="rec_name",
        compute="_compute_rec_name"
    )
    codigo_respuesta_id = fields.Many2one(
        comodel_name='fleet.tecno.peticion.respuesta',
        string="Codigo de respuesta",
    )
    codigo = fields.Char(
        string="Codigo"
    )
    mensaje = fields.Text(
        string="Mensaje",
    )
    resumen = fields.Char(
        string="Resumen",
    )

    def equivalencia(self,field):
        mapping = {
            0: 1,
            1: 2,
            10: 3,
            11: 4,
            12: 5,
            13: 6,
            14: 7,
            15: 8,
            16: 9,
            17: 10
        }
        return mapping.get(field, field)

    def enviar_peticion_tecno(self,contrato,accion,res):
        contrato = self.env['fleet.vehicle.log.contract'].search([('ins_ref','=', contrato)])
        vehiculo = contrato.vehicle_id
        url = self.env['ir.config_parameter'].sudo().get_param('fleet_tecnocontrol.admin_bloqueo')
        tcv_client = self.env['ir.config_parameter'].sudo().get_param('fleet_tecnocontrol.tcv_client_id')
        headers = {
            'Content-Type': 'application/json',
            'Tcv-Client-ID': tcv_client,
        }
        payload = [{
            'SERIE': vehiculo.vin_sn,
            'ACCION': accion,
        }]
        response = requests.post(url, headers=headers, json=payload)
        if response:
            data = response.json()
            res.write({
                'vehiculo_contrato_id': vehiculo.id,
                'vin_sn': vehiculo.vin_sn,
                'codigo': data[0]['CODIGO'],
                'mensaje': data[0]['MENSAJE'],
                'resumen': data[0]['RESUMEN'],
            })


    def equivalencia_operacion(self,field):
        mapping = {
            1:2,
            2:3
        }
        return mapping.get(field, field)

    def enviar_peticion(self,contrato,tipo_operacion,res):
        operacion = self.equivalencia_operacion(tipo_operacion)
        self.enviar_peticion_tecno(contrato,operacion, res)


    @api.model
    def create_custom(self,vals):
        res = self.create(self.dict_create(vals))
        self.enviar_peticion(vals['numeroContrato'],vals['tipoOperacion'],res)
        return res

    def dict_create(self,vals):
        estado = self.env['tecno.peticion.estado'].search([('name', '=', 'Pendiente')])
        return  {
            "estado_id": estado.id,
            "tipo_operacion": vals['tipoOperacion'],
            "numero_contrato": vals['numeroContrato'],
            "cod_area_solicitante": vals['codigoAreaSolicitante'],
            "id_usuario": vals['idUsuario'],
            "motivo_solicitud": vals['motivoSolicitud'],
            "fecha_hora_req": vals['fechaHoraRequerimiento'],
            "codigo_respuesta_id": self.equivalencia(vals['codigoRespuesta']),
        }

    def _compute_rec_name(self):
       for record in self:
           record.rec_name = f"{record.id}-{record.tipo_operacion.name}-{record.numero_contrato}"