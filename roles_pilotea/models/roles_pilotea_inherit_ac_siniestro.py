from odoo import fields,models,api

import logging
_logger = logging.getLogger(__name__)

class RolesPiloteaInheritACSiniestro(models.Model):
    _inherit = 'atencion.cliente.siniestro'


    @api.model
    def write(self, vals):
        fase_abierto = self.env['fleet.siniestro.fase'].search([('name', '=', 'Abierto')], limit=1)
        etapa_revision = self.env['fleet.siniestro.etapa'].search([('name', '=', 'Revisión')])
        poliza = self.env['fleet.poliza'].search([('vehiculo_id', '=', self.vehiculo_id.id), ('fecha_vencimiento', '>=', fields.Date.today())], limit=1)
        res = super().write(vals)
        estado_conclido = self.env['atencion.cliente.status.registro'].search([('name', '=', 'Concluido')])
        dictamen = False
        if self.tipo_siniestro_id.id == self.siniestro_robo.id:
            dictamen = 'robo'
        elif self.responsabilidad.name == 'Afectado':
            dictamen = 'afectado'
        elif self.responsabilidad.name == 'Responsable':
            dictamen = 'responsable'
        if 'estatus_registro_id' in vals and vals.get('estatus_registro_id') == estado_conclido.id:
            create = self.env['fleet.siniestro'].sudo().create({
                'fase_id': fase_abierto.id,
                'aseguradora_id': poliza.proveedor_id.id if poliza.proveedor_id else False,
                'siniestro_tipo_id': self.tipo_siniestro_id.id,
                'folio':self.num_reporte,
                'siniestro': self.num_siniestro,
                'vehiculo_id': self.vehiculo_id.id,
                'fecha_hora_suceso': self.fecha_ocurrido,
                'fecha_hora_notifiacion': self.fecha_reporte,
                'ubicacion': self.ubicacion,
                'conductor': self.conductor,
                'telefono_conductor': self.telefono_conductor,
                'descripcion_siniestro': self.detalle,
                'create_uid': self.env.user.id,
                'etapa_id': etapa_revision.id,
                'dictamen': dictamen
            })
            attachments = []
            ev_names = ['evidencia_1','evidencia_2','evidencia_3','evidencia_4']
            evidencias = self.env['ir.attachment'].sudo().search([('res_model','=', self._name),('res_id','=', self.id),('res_field','in',ev_names)])
            for att in evidencias:
                new_att = att.copy({
                    'res_model': 'fleet.siniestro',
                    'res_id': create.id,
                    'res_field': False,
                })
                attachments.append(new_att.id)
            self.env.cr.flush()
            create.message_post(
                body="Adjunto de archivos",
                attachment_ids = attachments
            )
            self.enviar_correo_siniestro()
        return res

    def enviar_correo_siniestro(self):
        plaza_registro = self.plaza_id.id
        flotilla_registro = self.vehiculo_id.flotilla_id.id
        group_names = [
            'Gerente de operaciones',
            'Auxiliar/Analista operaciones',
            'Gerente de mantenimiento',
            'Auxiliar de mantenimiento',
            'Ejecutivo atención a clientes',
            'Líder de atención a clientes',
        ]
        groups = self.env['res.groups'].search([('name', 'in', group_names)])
        users = self.env['res.users'].search([])
        if groups:
            users = users.filtered(lambda u: any(g.id in groups.ids for g in u.group_ids))
        if plaza_registro:
            users = users.filtered(lambda u: plaza_registro in u.plaza_ids.ids)
        if flotilla_registro:
            users = users.filtered(lambda u: flotilla_registro in u.flotilla_ids.ids)
        users = users.filtered(lambda u: u.email)
        rol_tipo_siniestro = self.env['roles.pilotea.exclusion.tipo'].search([('name','=','Siniestro')])
        datos = self.env['roles.pilotea.exclusion'].search_read([('tipo_exclusion_ids','in',[rol_tipo_siniestro.id])], fields=['correo'])
        correos_excluir = []
        for registro in datos:
            correos_excluir.append(registro['correo'])
        emails = users.mapped('email')
        emails = [e for e in emails if e not in correos_excluir]
        if emails:
            email_to = ','.join(emails)
            self.send_mail(self.id, email_to, 'atencion_cliente.atencion_cliente_siniestro_mail_template')

    def send_mail(self,res_id,email,name_template):
        template = self.env.ref(name_template)
        template.send_mail(
            res_id,
            force_send=True,
            email_values={
                'email_to': email
            }
        )