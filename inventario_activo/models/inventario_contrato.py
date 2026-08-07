from odoo import fields,models,api


class InventarioContrato(models.Model):
    _name = "inventario.contrato"
    _inherit = ["mail.thread","mail.activity.mixin"]

    name = fields.Char(
        string="Nombre",
        compute="_compute_nombre",
        store=True,
    )
    contrato_folio = fields.Char(
        string="Contrato",
    )
    fecha_inicio = fields.Date(
        string="Fecha Inicio",
    )
    fecha_fin = fields.Date(
        string="Fecha Fin",
    )
    periodo_arrendamiento = fields.Char(
        string="Periodo Arrendamiento",
    )
    nota = fields.Char(
        string="Nota",
    )
    etapa_id = fields.Many2one(
        string="Etapa",
        comodel_name="inventario.contrato.etapa",
    )
    # Documentos de  modelo
    contrato_attach = fields.Binary(
        string="Contrato",
    )
    factura_attach = fields.Binary(
        string="Factura",
    )

    @api.depends("contrato_folio")
    def _compute_nombre(self):
        for record in self:
            record.name = record.contrato_folio