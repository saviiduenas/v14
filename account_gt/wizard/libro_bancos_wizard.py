# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibroBancosWizard(models.TransientModel):
    _name = 'account_gt.libro_bancos.wizard'
    _description = "Wizard para libro de bancos"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    cuenta_id = fields.Many2one('account.account', string='Cuenta')


    def print_report(self):
        data = {
             'ids': [],
             'model': 'account_gt.libro_bancos.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_libro_bancos').report_action([], data=data)
