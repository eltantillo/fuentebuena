from odoo import fields,api,models
import io
import zipfile
import base64
import openpyxl

class DescargaMasiva(models.TransientModel):
    _name = 'descarga.masiva'
    _description = 'Descarga Masiva'

    vehiculo_ids = fields.Many2many(
        comodel_name='fleet.vehicle',
        string='Vehiculos',
    )
    modelo = fields.Selection([
        ('poliza', 'Póliza de seguro'),
        ('factura', 'Factura de vehículo'),
        ('placa', 'Alta de placas'),
        ('gps', 'GPS'),
        ('tenencia', 'Tenencia'),
        ('control_vehicular', 'Control vehicular'),
        ('tarjeta_circulacion', 'Tarjeta de circulación'),
    ],  string="Documento")
    excel_vines = fields.Binary(
        string="Carga tu excel"
    )

    #
    # @api.onchange('excel_vines')
    # def _onchange_excel_vines(self):
    #     if not self.excel_vines:
    #         self.vehiculo_ids = [(5,0,0)]
    #         return
    #     try:
    #         file_data = base64.b64decode(self.excel_vines)
    #         file_stream = io.BytesIO(file_data)
    #         workbook = openpyxl.load_workbook(file_stream)
    #         sheet = workbook.active



    def busqueda(self,nom_doc,vehiculo,fields):
        if nom_doc == 'factura':
            return self.env['fleet.vehicle'].search_read([('id', '=', vehiculo.id)], fields=fields, limit=1,  order='create_date desc')
        elif nom_doc == 'placa':
            return self.env['fleet.tramite'].search_read([('vehiculo_id', '=', vehiculo.id),('tipo_tramite_id', '=', 3)], fields=fields, limit=1,  order='create_date desc')
        elif nom_doc == 'gps':
            return self.env['fleet.adecuacion'].search_read([('vehiculo_id', '=', vehiculo.id),('adecuacion_id','=', 2)], fields=fields, limit=1,  order='create_date desc')
        elif nom_doc == 'poliza':
            return self.env['fleet.poliza'].search_read([('vehiculo_id','=',vehiculo.id)], fields=fields, limit=1,  order='create_date desc')
        elif nom_doc == 'tenencia':
            return self.env['fleet.tramite'].search_read([('vehiculo_id', '=', vehiculo.id),('tipo_tramite_id', '=', 6)], fields=fields, limit=1,  order='create_date desc')
        elif nom_doc == 'control_vehicular':
            return self.env['fleet.tramite'].search_read([('vehiculo_id', '=', vehiculo.id),('tipo_tramite_id', '=', 11)], fields=fields, limit=1,  order='create_date desc')
        elif nom_doc == 'tarjeta_circulacion':
            return self.env['fleet.tramite'].search_read([('vehiculo_id', '=', vehiculo.id),('tipo_tramite_id', '=', 4)], fields=fields, limit=1,  order='create_date desc')

    def action_descarga(self):
        if self.modelo == 'poliza':
            return self.ejecutar_accion('poliza',['id','attach_poliza','create_date', 'fecha_vencimiento'],'attach_poliza')
        elif self.modelo == 'factura':
            return self.ejecutar_accion('factura',['id','factura_vehiculo', 'create_date'], 'factura_vehiculo')
        elif self.modelo == 'placa':
            return self.ejecutar_accion('placa',  ['id', 'expediente', 'create_date', 'fecha_vencimiento_renovacion'], 'expediente')
        elif self.modelo == 'gps':
            return self.ejecutar_accion('gps',  ['id', 'expediente_arch', 'create_date'], 'expediente_arch')
        elif self.modelo == 'tenencia':
            return self.ejecutar_accion('tenencia', ['id', 'expediente', 'create_date', 'fecha_vencimiento_renovacion'], 'expediente')
        elif self.modelo == 'control_vehicular':
            return self.ejecutar_accion('control_vehicular', ['id', 'expediente', 'create_date', 'fecha_vencimiento_renovacion'], 'expediente')
        elif self.modelo == 'tarjeta_circulacion':
            return  self.ejecutar_accion('tarjeta_circulacion',['id', 'expediente', 'create_date', 'fecha_vencimiento_renovacion'], 'expediente')
        return True


    def ejecutar_accion(self,nom_doc,fields,nom_var):
        buffer = io.BytesIO()
        faltantes = []
        with zipfile.ZipFile(buffer, 'w') as zipf:
            for vehiculo in self.vehiculo_ids:
                documento = self.busqueda(nom_doc, vehiculo, fields)
                if documento:
                    data = documento[0].get(nom_var)
                    if data:
                        if nom_doc == 'poliza':
                            zipf.writestr(f"{nom_doc}_{vehiculo.vin_sn}_{documento[0].get('fecha_vencimiento')}.pdf", base64.b64decode(data))
                        elif nom_doc == 'factura' or nom_doc == 'gps':
                            zipf.writestr(f"{nom_doc}_{vehiculo.vin_sn}.pdf", base64.b64decode(data))
                        elif nom_doc == 'placa' or nom_doc == 'tenencia' or nom_doc == 'control_vehicular' or nom_doc == 'tarjeta_circulacion':
                            zipf.writestr(f"{nom_doc}_{vehiculo.vin_sn}_{documento[0].get('fecha_vencimiento_renovacion')}.pdf",base64.b64decode(data))
                    else:
                        faltantes.append(f"{vehiculo.vin_sn} sin archivo")
                else:
                    faltantes.append(f"{vehiculo.vin_sn} sin archivo encontrado")
            if faltantes:
                contenido = "\n".join(faltantes)
                zipf.writestr("faltantes.txt", contenido)
        buffer.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': f'{nom_doc}s.zip',
            'datas': base64.b64encode(buffer.read()),
            'mimetype': 'application/zip',
            'res_model': self._name,
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
