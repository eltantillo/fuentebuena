from odoo import fields,models,api



class ComplementoPago(models.Model):

    _name = 'complemento.pago'


    adecuacion_id = fields.Many2one(
        string='Adecuacion',
        comodel_name='fleet.adecuacion',
    )
    fleet_vehicle_id = fields.Many2one(
        string='Adecuacion',
        comodel_name='fleet.vehicle',
    )
    poliza_id = fields.Many2one(
        string='Adecuacion',
        comodel_name='fleet.poliza',
    )
    tramite_id = fields.Many2one(
        string='Adecuacion',
        comodel_name='fleet.tramite',
    )
    mantenimiento_id = fields.Many2one(
        string='Mantenimiento',
        comodel_name='fleet.mantenimiento',
    )

    xml = fields.Binary(
        string='XML'
    )

    pdf=fields.Binary(
        string='PDF'
    )