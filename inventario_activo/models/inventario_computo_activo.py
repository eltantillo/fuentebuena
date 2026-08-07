from odoo import fields,models,api


class InventarioComputoActivo(models.Model):
    _name = "inventario.computo.activo"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    etapa_id = fields.Many2one(
        comodel_name="inventario.computo.etapa",
        string="Etapa"
    )
    name = fields.Char(
        string="Nombre"
    )
    logo = fields.Binary(
        string="Logo",
    )
    #Datos del equipo
    validado = fields.Integer(
        string="Validado",
    )
    modelo_id = fields.Many2one(
        comodel_name="inventario.modelo",
        string="Modelo",
    )
    fabricante_id = fields.Many2one(
        comodel_name="inventario.fabricante",
        string="Fabricante",
    )
    proveedor_id = fields.Many2one(
        comodel_name="inventario.proveedor.activo",
        string="Proveedor",
    )
    estatus_id = fields.Many2one(
        comodel_name="inventario.estatus",
        string="Estatus de propiedad",
    )
    etiqueta_seguridad_num = fields.Char(
        string="Etiqueta seguridad",
    )
    active = fields.Boolean(
        string="Activado",
        default=True,
    )
    #baja
    fecha_baja = fields.Date(
        string="Fecha Baja",
    )
    motivo_baja = fields.Text(
        string="Motivo Baja",
    )
    #Información asignacion
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
    )
    puesto_id = fields.Many2one(
        comodel_name="hr.job",
        string="Puesto",
    )
    fecha_asignacion = fields.Date(
        string="Fecha asignacion",
    )
    fecha_ingreso_stock = fields.Date(
        string="Fecha ingreso stock"
    )
    ubicacion_stock_id = fields.Many2one(
        comodel_name="inventario.ubicacion",
        string="Ubicacion",
    )
    #Especificaciones
    procesador_id = fields.Many2one(
        comodel_name="inventario.computo.procesador",
        string="Procesador",
    )
    mac_wifi = fields.Char(
        string="MAC WiFi",
    )
    ram = fields.Integer(
        string="Ram",
    )
    generacion = fields.Char(
        string="Generacion",
    )
    almacenamiento = fields.Integer(
        string="Almacenamiento",
    )
    tipo_almacenamiento_id = fields.Many2one(
        comodel_name="inventario.computo.almacenamiento",
        string="Tipo almacenamiento",
    )
    doble_unidad = fields.Boolean(
        string="Doble unidad de almacenamiento",
    )
    #Adquisición
    contrato_id = fields.Many2one(
        comodel_name="inventario.contrato",
        string="Contrato arrendamiento",
    )
    importe = fields.Float(
        string="Importe",
    )
    iva = fields.Float(
        string="IVA",
    )
    total =fields.Float(
        string="Total",
    )
    esquema_ad_id = fields.Many2one(
        comodel_name="inventario.esquema.adquisicion",
        string="Esquema de Adquisicion",
    )
    #Garantia
    tipo_garantia_id = fields.Many2one(
        comodel_name="inventario.tipo.garantia",
        string="Tipo Garantia",
    )
    fecha_vigencia = fields.Date(
        string="Vigencia",
    )
    vigente = fields.Boolean(
        string="Vigente",
    )
    #Resguardo
    resguardo_attach = fields.Binary(
        string="Resguardo",
    )
    #Lógica
    mostrar_baja = fields.Boolean(
        string="Mostrar Baja",
        compute="_compute_mostrar_baja",
    )
    mostrar_stock = fields.Boolean(
        string="Mostrar Stock",
        compute="_compute_mostrar_stock",
    )
    mostrar_asignacion = fields.Boolean(
        string="Mostar Aignacion",
        compute="_compute_mostrar_asignacion",
    )

    def _compute_mostrar_baja(self):
        etapa_baja = self.env['inventario.computo.etapa'].search([('name', '=', 'BAJA')])
        for record in self:
            if record.etapa_id.id == etapa_baja.id:
                record.mostrar_baja = False
            else:
                record.mostrar_baja = True

    def _compute_mostrar_stock(self):
        etapa_stock = self.env['inventario.computo.etapa'].search([('name', '=', 'STOCK')])
        for record in self:
            if record.etapa_id.id == etapa_stock.id:
                record.mostrar_stock = False
            else:
                record.mostrar_stock = True

    def _compute_mostrar_asignacion(self):
        etapa_asinacion = self.env['inventario.computo.etapa'].search([('name', '=', 'ASIGNADO')])
        for record in self:
            if record.etapa_id.id == etapa_asinacion.id:
                record.mostrar_asignacion = False
            else:
                record.mostrar_asignacion = True