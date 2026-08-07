
from odoo import models,api,fields
from datetime import timedelta
import pytz
import logging
_logger = logging.getLogger(__name__)

class CMInheritMantenimiento(models.Model):
    _inherit = "fleet.mantenimiento"

    cita_ids = fields.One2many(
        comodel_name='cita.mantenimiento',
        string='Cita',
        inverse_name='mantenimiento_id',
    )

    def send_mail(self,res_id,email,name_template):
        template = self.env.ref(name_template)
        template.send_mail(
            res_id,
            force_send=True,
            email_values={
                'email_to': email
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        etapa_requerido = self.env["fleet.mantenimiento.etapa"].search([("name", "=", 'Requerido')], limit=1)
        mante_vh_preventivo = self.env['fleet.mantenimiento.tipo'].search([("name", "=", 'Vehicular Preventivo')], limit=1)
        res = super().create(vals_list)
        for vals, record in zip(vals_list, res):
            if 'etapa_id' in vals and 'tipo_mantenimiento_id' in vals:
                if (vals['etapa_id'] == etapa_requerido.id and vals['tipo_mantenimiento_id'] == mante_vh_preventivo.id):
                    email = record.vehiculo_id.driver_id.email
                    self.send_mail(record.id,email,'cita_mantenimiento.cm_invitacion_mail_template')
                else:
                    _logger.info("[CREATE_MANTENIMIENTO] ❌ Condición NO cumplida")
            else:
                _logger.info("[CREATE_MANTENIMIENTO] ❌ No vienen campos en vals")
        return res

    def return_etapa_mante(self,name):
        etapa = self.env['fleet.mantenimiento.etapa'].search([('name', '=', name)])
        return etapa

    def return_tipo_mante(self,name):
        tipo = self.env['fleet.mantenimiento.tipo'].search([('name', '=', name)])
        return tipo

    def comprobar_cita_vinculada(self):
        zona_local = pytz.timezone('America/Mexico_City')
        etapa_requerido = self.return_etapa_mante('Requerido')
        tipo_mantenimiento = self.return_tipo_mante('Vehicular Preventivo')
        mantenimientos = self.env['fleet.mantenimiento'].search([
            ('etapa_id', '=', etapa_requerido.id),
            ('tipo_mantenimiento_id', '=', tipo_mantenimiento.id)
        ])
        for record in mantenimientos:
            fecha_prevista_agenda = record.create_date + timedelta(days=1)
            fecha_utc = pytz.utc.localize(fecha_prevista_agenda)
            fecha_local_agenda = fecha_utc.astimezone(zona_local)
            ahora_utc = pytz.utc.localize(fields.Datetime.now())
            ahora_local = ahora_utc.astimezone(zona_local)
            if fecha_local_agenda <= ahora_local:
                existe_cita = self.env['cita.mantenimiento'].search([
                    ('mantenimiento_id', '=', record.id)
                ], limit=1)
                if not existe_cita:
                    # self.env['cita.mantenimiento'].create({
                    #     'mantenimiento_id': record.id,
                    #     'cita_creada_automaticamente': True
                    # })
                    # self.env.cr.commit()
                    try:
                        response = self.env['cita.mantenimiento'].create_simplybook(record.id, False)
                    except Exception as e:
                        _logger.error("[ID %s] Error crítico al intentar crear cita: %s", record.id, str(e))
                else:
                    _logger.info("[ID %s] Salto: Ya existe cita vinculada (Cita ID: %s)", record.id, existe_cita.id)
            else:
                tiempo_restante = fecha_local_agenda - ahora_local
                _logger.info("[ID %s] En espera: Faltan %s para cumplir las 24h", record.id, tiempo_restante)
        _logger.info("== FINALIZACIÓN DE VERIFICACIÓN DE CITAS ==")