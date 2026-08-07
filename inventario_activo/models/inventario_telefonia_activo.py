from odoo import fields,models,api


class InventarioTelefoniaActivo(models.Model):
    _name = "inventaro.telefonia.activo"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre"
    )
    logo = fields.Binary(
        string="Logo",
    )
    etapa_id = fields.Many2one(
        comodel_name="inventario.telefonia.etapa",
        string="Etapa",
    )
    color = fields.Integer(
        string="Color",
    )
    imei = fields.Char(
        string="IMEI",
    )
    linea_asignada = fields.Char(
        string="Linea Asignada",
    )
    modelo_id = fields.Many2one(
        comodel_name="inventario.modelo",
        string="Modelo"
    )
    fabricante_id = fields.Many2one(
        comodel_name="inventario.fabricante",
        string="Fabricante",
    )
    proveedor_id = fields.Many2one(
        comodel_name="inventario.proveedor.activo",
        string="Proveedor",
    )
    active = fields.Boolean(
        string="Activo",
    )
    #baja
    fecha_baja = fields.Date(
        string="Fecha Baja",
    )
    motivo_baja = fields.Text(
        string="Motivo Baja",
    )
    #información asignación
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
    )
    puesto_id = fields.Many2one(
        comodel_name="hr.job",
        string="Puesto",
    )
    fecha_asignacion = fields.Date(
        string="Fechas Asignacion",
    )
    fecha_ingreso_stock = fields.Date(
        string="Fecha ingreso stock"
    )
    ubicacion_stock_id = fields.Many2one(
        comodel_name="inventario.ubicacion",
        string="Ubicacion",
    )
    #especificaciones
    memoria_ram = fields.Integer(
        string="Memoria Ram",
    )
    mac_wifi = fields.Char(
        string="Mac WiFi",
    )
    almacenamiento = fields.Integer(
        string="Almacenamiento",
    )
    capacidad_bateria = fields.Integer(
        string="Capacidad Bateria",
    )
    camara = fields.Char(
        string="Camara",
    )
    #adquisicion
    fecha_adquisicion = fields.Date(
        string="Fecha Adquisicion",
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
    num_plazos = fields.Integer(
        string="Numero de plazos",
    )
    #Resguardo Attach
    resguardo_attach = fields.Integer(
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
        etapa_baja = self.env['inventario.telefonia.etapa'].search([('name', '=', 'BAJA')])
        for record in self:
            if record.etapa_id.id == etapa_baja.id:
                record.mostrar_baja = False
            else:
                record.mostrar_baja = True

    def _compute_mostrar_stock(self):
        etapa_stock = self.env['inventario.telefonia.etapa'].search([('name', '=', 'STOCK')])
        for record in self:
            if record.etapa_id.id == etapa_stock.id:
                record.mostrar_stock = False
            else:
                record.mostrar_stock = True

    def _compute_mostrar_asignacion(self):
        etapa_asignacion = self.env['inventario.telefonia.etapa'].search([('name', '=', 'ASIGNADO')])
        for record in self:
            if record.etapa_id.id == etapa_asignacion.id:
                record.mostrar_asignacion = False
            else:
                record.mostrar_asignacion = True