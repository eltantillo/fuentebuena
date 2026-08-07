from odoo import fields,models,api


class PromesaPPromesa(models.Model):
    _name='promesa.p.promesa'
    _rec_name = 'rec_name'
    _inherit = ["mail.thread","mail.activity.mixin"]
    _order = "id desc"

    gestor_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Gestor",
    )
    fecha_gestion = fields.Date(
        string="Fecha de gestion",
    )
    importe_promesa = fields.Float(
        string="Importe promesa",
    )
    fecha_compromiso = fields.Date(
        string="Fecha compromiso",
    )
    estatus_promesa = fields.Many2one(
        comodel_name='promesa.p.ecv.promesa.pago',
        string="Estatus promesa",
    )
    periodo_nomina_id = fields.Many2one(
        comodel_name='promesa.p.periodo.nom.convenio',
        string="Periodo nomina",
    )
    convenio_id = fields.Many2one(
        comodel_name='promesa.p.convenio',
        string="Convenio",
    )
    nombre_promitente = fields.Char(
        string="Nombre promiente",
    )
    cargo_promitente = fields.Char(
        string="Cargo promiente",
    )
    fecha_cumplimiento = fields.Date(
        string="Fecha cumplimiento",
    )
    suma_total_pagos = fields.Float(
        string="Suma total pagos",
    )
    estatus_cumplimiento = fields.Many2one(
        string="Estatus cumplimiento",
        comodel_name='promesa.p.estado.cumplimiento',
    )
    monto_por_pagar = fields.Float(
        string="Monto por pagar",
    )
    gestores = fields.Many2many(
        comodel_name='hr.employee',
        string="Gestores",
        compute='_compute_gestores',
    )
    pago_ids = fields.One2many(
        comodel_name='promesa.p.pago',
        string="Pagos",
        inverse_name='promesa_id',
    )
    rec_name = fields.Char(
        string="res_name",
        compute='_compute_rec_name',
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.convenio_id.name}"

    def _compute_gestores(self):
        for record in self:
            rol = self.env['promesa.p.rol'].search([('name', '=', 'Gestores')], limit=1)
            if rol:
                record.gestores = [(6, 0, rol.employee_ids.ids)]
            else:
                record.gestores = [(5, 0, 0)]