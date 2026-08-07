from odoo import api,models,fields


class PromesaPPago(models.Model):
    _name = 'promesa.p.pago'
    _rec_name = 'id'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    promesa_id = fields.Many2one(
        comodel_name='promesa.p.promesa',
        string="Promesa",
    )
    fecha_pago = fields.Date(
        string="Fecha de Pago",
    )
    importe_pago = fields.Float(
        string="Importe pago",
    )
    banco_id = fields.Many2one(
        string="Banco",
        comodel_name='promesa.p.ins.financiera',
    )
    numero_cuenta = fields.Char(
        string="Numero de cuenta",
    )
    cie = fields.Char(
        string="CIE",
    )
    referencia = fields.Char(
        string="Referencia",
    )
    referencia_dos = fields.Char(
        string="Referencia dos",
    )
    observaciones = fields.Char(
        string="Observaciones",
    )
    comprobante_attach = fields.Binary(
        string="Comprobante",
        attachment=True,
    )
    active = fields.Boolean('Active', default=True, tracking=True)