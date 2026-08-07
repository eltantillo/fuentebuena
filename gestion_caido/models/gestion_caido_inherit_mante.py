from odoo import fields,models,api

class GestionCaidoInheritMante(models.Model):

    _inherit = "fleet.mantenimiento"

    def write(self, vals):
        modelGestion = self.env['gestion.caido']
        gestion_vinculada = modelGestion.search([('mante_ligado_id', '=', self.id)])
        etapa_programado = self.env['fleet.mantenimiento.etapa'].search([('name', '=', 'Programado')], limit=1).id
        etapa_finalizado = self.env['fleet.mantenimiento.etapa'].search([('name', '=', 'Finalizado')], limit=1).id
        res = super(GestionCaidoInheritMante, self).write(vals)
        if gestion_vinculada:
            if 'etapa_id' in vals:
                if vals['etapa_id'] == etapa_programado:
                    gestion_vinculada.registrar_evento(f"Mantenimiento Programado para: {self.fecha_programado}")
                elif vals['etapa_id'] == etapa_finalizado:
                    gestion_vinculada.registrar_evento(f"Mantenimiento Finalizado", True)
        return res