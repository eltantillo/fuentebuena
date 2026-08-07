from odoo import fields,models,api


class PromesaPProyeccionCobranza(models.Model):
    _name='promesa.p.proyeccion.cobranza'
    _rec_name = 'rec_name'
    _inherit = ["mail.thread","mail.activity.mixin"]
    _order = "id desc"

    convenio_id = fields.Many2one(
        comodel_name='promesa.p.convenio',
        string='Convenio',
    )
    periodo_gestion = fields.Char(
        string='Periodo gestion',
    )
    total = fields.Float(
        string='Total',
    )
    exigible_total = fields.Float(
        string='Exigible total',
    )
    factible_presupuesto = fields.Float(
        string='Factible presupuesto',
    )
    factible = fields.Float(
        string='Factible',
    )
    gestor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Gestor',
    )
    gestores = fields.Many2many(
        comodel_name='hr.employee',
        compute='_compute_gestores',
    )
    rec_name = fields.Char(
        string='Rec name',
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