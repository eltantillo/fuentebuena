from odoo import fields,models,api

class InventarioImpresoraActivo(models.Model):
    _name = "inventario.impresora.activo"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
    )
    modelo_id = fields.Many2one(
        comodel_name="inventario.modelo",
        string="Modelo",
    )
    fabricante_id = fields.Many2one(
        comodel_name="inventario.fabricante",
        String="Fabricante",
    )
    proveedor_id = fields.Many2one(
        comodel_name="inventario.proveedor.activo",
        string="Proveedor",
    )
    serie = fields.Char(
        string="Serie",
    )
    ubicacion_id = fields.Many2one(
        comodel_name="inventario.ubicacion",
        string="Ubicación",
    )
    estatus_id = fields.Many2one(
        comodel_name="inventario.estatus",
        string="Estatus"
    )
    activo = fields.Boolean(
        string="Activo",
    )
    #Baja
    motivo_baja = fields.Text(
        string="Motivo de baja",
    )
    fecha_baja = fields.Date(
        string="Fecha de baja",
    )
    #Especificaciones
    conectividad_id = fields.Many2one(
        comodel_name="inventario.impresora.conectividad",
        string="Conectividad",
    )
    ip = fields.Char(
        string="IP",
    )
    adf = fields.Boolean(
        string="ADF",
    )
    color = fields.Boolean(
        string="¿Color?",
    )
    tipo_consumible_id = fields.Many2one(
        comodel_name="inventario.impresora.consumible",
        string="Tipo de consumible",
    )
    modelo_consumible = fields.Char(
        string="Modelo de consumible",
    )
    #Información asignación
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
    )
    puesto_id = fields.Many2one(
        comodel_name="hr.job",
        string="Puesto",
    )
    fecha_asignacion = fields.Date(
        string="Fecha de asignacion",
    )
    #observaciones
    obsevacion = fields.Text(
        string="Observación",
    )
    #Adquisición
    fecha_adquisicion = fields.Date(
        string="Fecha de adquisicion",
    )
    importe =fields.Float(
        string="Importe",
    )
    iva = fields.Float(
        string="IVA",
    )
    total = fields.Float(
        string="Total",
    )
    esquema_ad_id = fields.Many2one(
        comodel_name="inventario.esquema.adquisicion",
        string="Esquema aquisición",
    )
    num_plazos = fields.Char(
        string="Número plazos",
    )
    #Garantía
    tipo_garantia_id = fields.Many2one(
        comodel_name="inventario.tipo.garantia",
        string="Tipo de garantia",
    )
    vigencia = fields.Date(
        string="Vigencia",
    )
    vigente = fields.Boolean(
        string="¿Vigente?",
    )
    #Evidencia fotografica
    evidencia_foto = fields.Binary(
        string="Evidencia fotografica",
    )
    #Resguardo
    resguardo_attach = fields.Binary(
        string="Resguardo",
    )
    etapa_id = fields.Many2one(
        comodel_name="inventario.impresora.etapa",
        string="Etapa",
    )
    etapa_baja_id = fields.Many2one(
        comodel_name="inventario.impresora.etapa",
        string="Etapa",
        compute="_compute_etapa_baja",
    )

    def _compute_etapa_baja(self):
        etapa_baja = self.env['inventario.impresora.etapa'].search([('name','=','Baja')], limit=1)
        for record in self:
            record.etapa_baja_id = etapa_baja.id
