# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import fields, models


class ViewList(models.Model):
    """
        A class to manage the access of views.
    """
    _name = "sh.view.list"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Holds All Available Views"

    name = fields.Char("Name", tracking=True)
    technical_name = fields.Char("Tech Name", tracking=True)
    