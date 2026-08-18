from odoo import fields,models,api


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
        string="Poliza"
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
        string="Tipo de tramites",
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

    @api.model
    def return_dict_expe(self,id):
        tipo = self.sudo().browse(id)
        requireds = []
        if tipo.factura_req:
            requireds.append('factura')
        elif tipo.opcion_compra_req:
            requireds.append('opcion_compra')
        elif tipo.poliza_req:
            requireds.append('poliza')
        elif tipo.endoso_req:
            requireds.append('endoso')
        elif tipo.contrato_req:
            requireds.append('contrato')
        elif tipo.tipo_tramite_ids:
            for record in tipo.tipo_tramite_ids:
                requireds.append(record.name)
        elif tipo.tipo_adecuacion_ids:
            for record in tipo.tipo_adecuacion_ids:
                requireds.append(record.name)
        return  requireds


    def notificar_gc(self):
        tipos = self.search([('notificar_por_correo','=','True')])
        vehiculos = self.env['fleet.vehicle'].search([('flotilla_id','=',1)])
        for record in tipos:
            documentos_req = self.return_dict_expe(record.id)

