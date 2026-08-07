from odoo import fields, api, models

class FleetOrdenCompra(models.Model):
    _name = "fleet.orden.compra"
    _description = "Ordenes de compra de vehículos"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'


    name = fields.Char(
        string="Nombre"
    )
    fecha_solicitud = fields.Date(
        string="Fecha de solicitud",
        default=fields.Date.today()
    )
    categoria_id = fields.Many2one(
        comodel_name="fleet.compra.categoria",
        string="Categoría"
    )
    proveedor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Proveedor",
    )
    razon_social_ids = fields.Many2many(
        comodel_name = "res.partner",
        string="Razones sociales",
        compute="_compute_razon_social_ids",
    )
    condicion_id = fields.Many2one(
        comodel_name = "fleet.compra.condicion",
        string="Condición"
    )
    etapa_id = fields.Many2one(
        comodel_name = "fleet.compra.etapa",
        string="Etapa",
        default=lambda self: self.env['fleet.compra.etapa'].search([('name', '=', 'Borrador')], limit=1)
    )
    nota = fields.Char(
        string="Notas"
    )
    sub_total = fields.Float(
        string="Subtotal",
        compute="_compute_totales",
        store=True
    )
    iva = fields.Float(
        string="IVA",
        compute="_compute_totales",
        store=True
    )
    total = fields.Float(
        string="Total",
        compute="_compute_totales",
        store=True
    )
    line_ids = fields.One2many(
        comodel_name = "fleet.orden.compra.line",
        string="Lineas de orden de compra",
        inverse_name = "orden_compra_id"
    )
    vehiculo_ids = fields.One2many(
        comodel_name = "fleet.vehicle",
        string="Vehículos",
        inverse_name = "orden_compra_id"
    )
    total_unidades = fields.Integer(
        string="Total de unidades"
    )
    total_vehiculos = fields.Float(
        string="Total de vehículos"
    )
    proveedor_coches = fields.Many2one(
        comodel_name = "proveedor.tipo",
        string="Proveedor de compra de coches",
        compute="_compute_proveedor",
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    def _compute_proveedor(self):
        tipo = self.env['proveedor.tipo'].search([('name', '=', 'Compra de vehículos')], limit=1)
        self.proveedor_coches = tipo.id

    @api.depends('proveedor_id')
    def _compute_razon_social_ids(self):
        for record in self:
            record.razon_social_ids = record.proveedor_id.razones_sociales_ids.ids

    @api.depends('line_ids')
    def _compute_totales(self):
        for record in self:
            sub_total = 0
            iva = 0
            total = 0
            for line in record.line_ids:
                sub_total += line.importe
                iva += line.iva
                total += line.total
            record.sub_total = sub_total
            record.iva = iva
            record.total = total

    def alta_vehiculo(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "alta.vehiculo",
            "name": "Alta vehículo",
            "view_mode": "form",
            "target": "new",
            "view_id": self.env.ref("fleet_compra.fleet_orden_compra_alta_vehiculo_view_form").id,
            "context": {'default_proveedor_id': self.proveedor_id.id},
        }

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('x_orden_compra_seq') or 'OC-00000'
        return super().create(vals_list)