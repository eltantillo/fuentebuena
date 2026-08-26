from odoo import fields,models,api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ExpedienteTipo(models.Model):

    _name = 'expediente.tipo'

    name = fields.Char(
        string="Nombre"
    )
    #Archivos Vehículo
    factura_req = fields.Boolean(
        string="Factura"
    )
    opcion_compra_req = fields.Boolean(
        string="Opción a compra"
    )
    #Pólizas
    poliza_req = fields.Boolean(
        string="Póliza"
    )
    endoso_req = fields.Boolean(
        string="Endoso"
    )
    #Contrato
    contrato_req = fields.Boolean(
        string="Contrato"
    )
    #Tramites
    tipo_tramite_ids = fields.Many2many(
        string="Tipo de trámites",
        comodel_name="fleet.tramite.tipo",
    )
    #Adecuaciones
    tipo_adecuacion_ids = fields.Many2many(
        string="Tipo de Adecuaciones",
        comodel_name="fleet.adecuacion.catalogo"
    )
    notificar_por_correo = fields.Boolean(
        string="Notificar",
    )
    usuarios_notificar_ids = fields.Many2many(
        string="Usuarios notificar",
        comodel_name='hr.employee',
    )
    expediente_principal = fields.Boolean(
        string="Expediente principal",
    )


    @api.model
    def return_documents(self):
        expe_principal = self.search([('expediente_principal','=','True')])
        required_doc = self.return_dict_expe(expe_principal.id)
        return required_doc


    @api.constrains('expediente_principal')
    def _check_expediente_principal(self):
        for record in self:
            if not record.expediente_principal:
                continue

            expe = self.search_count([
                ('expediente_principal', '=', True),
                ('id', '!=', record.id),
            ])
            if expe:
                raise ValidationError(
                    'Solo se puede tener un expediente principal.'
                )

    @api.model
    def return_dict_expe(self,id):
        tipo = self.sudo().browse(id)
        requireds = []
        if tipo.factura_req:
            requireds.append('Factura')
        if tipo.opcion_compra_req:
            requireds.append('Opción a compra')
        if tipo.poliza_req:
            requireds.append('Póliza')
        if tipo.endoso_req:
            requireds.append('Endoso')
        if tipo.contrato_req:
            requireds.append('Contrato')
        if tipo.tipo_tramite_ids:
            for record in tipo.tipo_tramite_ids:
                requireds.append(record.name)
        if tipo.tipo_adecuacion_ids:
            for record in tipo.tipo_adecuacion_ids:
                requireds.append(f'Adecuación: {record.name}')
        return  requireds


    def notificar_gc(self):
        tipos = self.search([('notificar_por_correo','=','True')])
        vehiculos = self.env['fleet.vehicle'].search([('flotilla_id','=',1)])
        for record in tipos:
            documentos_req = self.return_dict_expe(record.id)

