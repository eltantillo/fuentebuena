# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import json
import logging
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import ustr
import requests
import pytz
import time

class FbIntegrationLog(models.Model):

    _name = 'fb.integration.log'
    _description = 'FB Integracion Logs'
    _inherit = ["mail.thread.main.attachment", "mail.activity.mixin"]  # Habilitamos el chatter para auditoría

    name = fields.Char(string='Peticion', default='New', required=True)
    data = fields.Text(string='Datos', required=True)
    #data_ticket_request = fields.Text(string='Datos tickest')

    #order_count = fields.Integer(string='Cantidad de Pedidos',compute='_compute_order_count')
    #response = fields.Text(string='Respuesta Api')
    notes = fields.Text(string='Notas')
    # state = fields.Selection([("request_received", "Peticion recibida"), ("processed", "Procesada"),
    #     ("response_sent", "Respuesta enviada"), ("response_error", "Error envio respuesta")], string="Estado", readonly=True,
    #     tracking=True, default="request_received")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('fb.integration.log') or '/'
        res = super().create(vals_list)
        return res