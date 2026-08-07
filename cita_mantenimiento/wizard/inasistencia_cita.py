from odoo import models,api,fields
import logging
_logger = logging.getLogger(__name__)

class InasistenciaCita(models.TransientModel):
    _name = 'inasistencia.cita'

    etapa_inasistencia_id = fields.Many2one(
        comodel_name='cita.mantenimiento.etapa',
        string='Etapa',
        compute='_compute_etapa_inasistencia_id',
    )

    def _compute_etapa_inasistencia_id(self):
        etapa_inasistencia_id = self.env['cita.mantenimiento.etapa'].search([('name','=', 'Inasistencia')])
        for record in self:
            record.etapa_inasistencia_id = etapa_inasistencia_id.id

    def confirmar(self):
        citas_ids = self.env.context.get('default_cita_ids')
        if not citas_ids:
            return
        citas = self.env['cita.mantenimiento'].search([('id', 'in', citas_ids)])
        citas.sudo().write({
            'etapa_id': self.etapa_inasistencia_id.id
        })