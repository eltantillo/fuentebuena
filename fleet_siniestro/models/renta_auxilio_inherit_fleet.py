from odoo import fields,models,api


class RentaAuxilioInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    renta_auxilio_ids = fields.One2many(
        comodel_name='fleet.siniestro.renta.auxilio.track',
        inverse_name='vehiculo_renta_id',
        string='Siniestros'
    )

    mostrar_terminar_renta = fields.Boolean(
        string='Mostrar terminar renta',
        compute='_compute_terminar_renta_auxilio',
    )

    mostrar_renta_aux = fields.Boolean(
        string='Mostrar renta auxilio',
        compute='_compute_mostrar_renta_auxilio'
    )

    mostrar_page_renta_aux = fields.Boolean(
        string='Mostrar page renta auxilio',
        compute='_compute_mostrar_page_renta_aux',
    )

    def _compute_terminar_renta_auxilio(self):
        etapa_prestado = self.env['fleet.vehicle.state'].search([('name','=','En préstamo')], limit=1)
        producto_renta = self.env['fleet.customer.producto'].search([('name','=','Renta Auxilio')], limit=1)
        for record in self:
            if record.producto_id.id == producto_renta.id and record.state_id.id == etapa_prestado.id:
                record.mostrar_terminar_renta = False
            else:
                record.mostrar_terminar_renta = True

    def _compute_mostrar_renta_auxilio(self):
        etapa_disponible = self.env['fleet.vehicle.state'].search([('name','=','Disponible')], limit=1)
        producto_renta = self.env['fleet.customer.producto'].search([('name','=','Renta Auxilio')], limit=1)
        if self.producto_id.id == producto_renta.id and self.state_id.id == etapa_disponible.id:
            self.mostrar_renta_aux = False
        else:
            self.mostrar_renta_aux = True


    def _compute_mostrar_page_renta_aux(self):
        producto_renta = self.env['fleet.customer.producto'].search([('name', '=', 'Renta Auxilio')], limit=1)
        for record in self:
            if record.producto_id.id == producto_renta.id:
                record.mostrar_page_renta_aux = False
            else:
                record.mostrar_page_renta_aux = True

    def return_terminar_renta_auxilio(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'terminar.renta.auxilio',
            'name': 'Terminar Renta Auxilio',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_siniestro.fleet_siniestro_terminar_renta_auxilio_form').id,
            'context': {'default_vehiculo_id': self.id }
        }