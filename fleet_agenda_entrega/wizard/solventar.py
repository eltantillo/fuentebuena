from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class SolventarWizard(models.TransientModel):
    _name = "evento.solventar.wizard"

    descripcion_solventacion = fields.Text(
        string="Descripción de solventación",
    )
    descripcion = fields.Text(
        string="Descripción de anomalía",
        compute="_compute_descripcion",
    )

    def _compute_descripcion(self):
        active_id = self.env.context.get('active_id')
        for record in self:
            evento = self.env['agenda.entrega.evento'].search([('id', '=', active_id)])
            record.descripcion = evento.descripcion

    def action_solventar(self):
        active_id = self.env.context.get('active_id')
        evento = self.env['agenda.entrega.evento'].search([('id', '=', active_id)])
        evento.write({
            'descripcion_solventacion': self.descripcion_solventacion,
            'status_id': 4
        })