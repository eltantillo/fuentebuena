from odoo import fields, models, api

class FleetOrdenCompraLine(models.Model):
    _name = "fleet.orden.compra.line"
    _description = "Ordenes de compra de vehículos lines"

    orden_compra_id = fields.Many2one(
        comodel_name = "fleet.orden.compra",
        string="Orden de compra",
    )
    model_id = fields.Many2one(
        comodel_name = "fleet.vehicle.model",
        string="Modelo"
    )
    year = fields.Char(
        string="Año"
    )
    transmision = fields.Selection(
        selection=[
            ('automatic', 'Automática'),
            ('manual', 'Manual')
        ],
        string="Transmisión"
    )
    gnv = fields.Boolean(
        string="GNV"
    )
    unidad = fields.Integer(
        string="Unidad"
    )
    precio_unitario = fields.Float(
        string="Precio unitario"
    )
    descuento = fields.Float(
        string="Descuento"
    )
    importe = fields.Float(
        string="Importe",
        compute='_compute_importe',
        store=True
    )
    iva = fields.Float(
        string="IVA",
        store = True
    )
    costo_gnv = fields.Float(
        string="Costo gnv"
    )
    auto_gnv = fields.Float(
        string="Auto + GNV",
        compute ='_compute_auto_gnv',
        store=True
    )
    total = fields.Float(
        string="Total",
        compute='_compute_total',
        store=True
    )
    fecha_requerida = fields.Date(
        string="Fecha requerida"
    )
    unidades_recibidas = fields.Integer(
        string="Unidades recibidas"
    )

    @api.depends('unidad', 'precio_unitario')
    def _compute_importe(self):
        for record in self:
            record.importe = (record.unidad or 0) * (record.precio_unitario + record.costo_gnv or 0)

    @api.depends('importe')
    def _compute_iva(self):
        for record in self:
            record.iva = (record.importe or 0) * .16

    @api.depends('importe','iva','descuento')
    def _compute_total(self):
        for record in self:
            record.total = (record.importe + record.iva) - record.descuento

    @api.depends('costo_gnv','unidad','precio_unitario')
    def _compute_auto_gnv(self):
        for record in self:
            record.auto_gnv = record.precio_unitario + record.costo_gnv