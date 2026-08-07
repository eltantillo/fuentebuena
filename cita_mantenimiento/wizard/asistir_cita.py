from odoo import models,api,fields
import logging
_logger = logging.getLogger(__name__)

class AsistirCita(models.TransientModel):
    _name = 'asistir.cita'

    etapa_asistida_id = fields.Many2one(
        comodel_name='cita.mantenimiento.etapa',
        string='Etapa',
        compute='_compute_etapa_asistida_id',
    )

    def _compute_etapa_asistida_id(self):
        etapa_asistida_id = self.env['cita.mantenimiento.etapa'].search([('name','=', 'Asistida')])
        for record in self:
            record.etapa_asistida_id = etapa_asistida_id.id

    def confirmar(self):
        citas_ids = self.env.context.get('default_cita_ids')
        if not citas_ids:
            return
        citas = self.env['cita.mantenimiento'].search([('id', 'in', citas_ids)])
        citas.sudo().write({
            'etapa_id': self.etapa_asistida_id.id
        })