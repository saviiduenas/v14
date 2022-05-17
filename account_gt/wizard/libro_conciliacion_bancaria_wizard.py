# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibroConciliacionBancariaWizard(models.TransientModel):
    _name = 'account_gt.libro_conciliacion_bancaria.wizard'
    _description = "Wizard para libro conciliacion bancaria"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    cuenta_id = fields.Many2one('account.account', string='Cuenta')
    saldo = fields.Float('Saldo de cuenta')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'account_gt.libro_conciliacion_bancaria.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_libro_conciliacion_bancaria').report_action([], data=data)
