from odoo import fields,models,api


class IntegracionBaseInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    external_gps_id = fields.Char(
        string="External GPS Id"
    )
    external_estado_bloqueo = fields.Selection(
        string="Estado de bloqueo",
        selection=[
            ('bloqueado', 'Bloqueado'),
            ('desbloqueado', 'Desbloqueado')
        ]
    )
    external_ubicacion = fields.Char(
        string="Ubicacion",
        compute='_compute_ubicacion',
        store=True,
    )
    external_longitud = fields.Char(
        string="Longitud",
    )
    external_latitud = fields.Char(
        string="Latitud",
    )
    external_gps_provider = fields.Selection(
        string="Proveedor GPS",
        selection=[]
    )
    mostrar_btn_bloqueo = fields.Boolean(
        string="Mostrar Bloqueo",
        compute='_compute_mostrar_btn_bloqueo',
    )
    mostrar_btn_desbloqueo = fields.Boolean(
        string="Mostrar Bloqueo",
        compute='_compute_mostrar_btn_desbloqueo',
    )
    mostrar_msj_bloqueo = fields.Boolean(
        string="Mostrar Mensaje Bloqueo",
        compute='_compute_mostrar_msj_bloqueo',
    )
    mostrar_msj_desbloqueo = fields.Boolean(
        string="Mostrar Mensaje Bloqueo",
        compute='_compute_mostrar_msj_desbloqueo',
    )

    def _compute_mostrar_msj_bloqueo(self):
        for record in self:
            existe = self.env['integracion.base.bloqueo'].search([
                ('vehiculo_id','=',self.id),
                ('tipo','=','bloqueo'),
                ('estado_peticion','=', 'registrado')
            ])
            if existe:
                record.mostrar_msj_bloqueo = False
            else:
                record.mostrar_msj_bloqueo = True

    def _compute_mostrar_msj_desbloqueo(self):
        for record in self:
            existe = self.env['integracion.base.bloqueo'].search([
                ('vehiculo_id','=',self.id),
                ('tipo','=','desbloqueo'),
                ('estado_peticion','=', 'registrado')
            ])
            if existe:
                record.mostrar_msj_desbloqueo = False
            else:
                record.mostrar_msj_desbloqueo = True

    def _compute_mostrar_btn_bloqueo(self):
        bloqueos_regis = self.env['integracion.base.bloqueo'].search([
            ('estado_peticion','=','registrado'),
            ('tipo','=','bloqueo')
        ])
        bloq_reg_map = {
            b.vehiculo_id.id: b for b in bloqueos_regis
        }
        for record in self:
            if record.external_estado_bloqueo == 'desbloqueado':
                bloque_activo = bloq_reg_map.get(record.id)
                if bloque_activo:
                    record.mostrar_btn_bloqueo = True
                else:
                    record.mostrar_btn_bloqueo = False
            else:
                record.mostrar_btn_bloqueo = True

    def _compute_mostrar_btn_desbloqueo(self):
        desbloqueos_regis = self.env['integracion.base.bloqueo'].search([
            ('estado_peticion','=','registrado'),
            ('tipo','=','desbloqueo')
        ])
        desbloq_reg_map = {
            b.vehiculo_id.id: b for b in desbloqueos_regis
        }
        for record in self:
            if record.external_estado_bloqueo == 'bloqueado':
                bloque_activo = desbloq_reg_map.get(record.id)
                if bloque_activo:
                    record.mostrar_btn_desbloqueo = True
                else:
                    record.mostrar_btn_desbloqueo = False
            else:
                record.mostrar_btn_desbloqueo = True

    @api.depends('external_latitud','external_longitud')
    def _compute_ubicacion(self):
        for record in self:
            record.external_ubicacion = f"{record.external_latitud},{record.external_longitud}"

    def bloquear_vehiculo(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'peticion.bloqueo',
            'name': 'Bloquear Vehículo',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_integracion_base.peticion_bloqueo_view_form').id,
            'context': {'default_vehiculo_id': self.id, 'default_type': "bloqueo"}
        }

    def desbloquear_vehiculo(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'peticion.bloqueo',
            'name': 'Desbloquear Vehículo',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_integracion_base.peticion_bloqueo_view_form').id,
            'context': {'default_vehiculo_id': self.id, 'default_type': "desbloqueo"}
        }