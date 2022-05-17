# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    cantidad_alumnos = fields.Integer('Cantidad alumnos')
