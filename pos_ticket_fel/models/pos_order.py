# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

class PosOrder(models.Model):
    _inherit = "pos.order"

    acceso = fields.Char("Numero de acceso")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        if 'acceso' in ui_order:
            res['acceso'] = ui_order['acceso']
        return res
