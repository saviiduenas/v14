# -*- encoding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
import logging

class LibroBancos(models.AbstractModel):
    _name = 'report.account_gt.reporte_libro_bancos'


    def saldo_inicial(self, datos):
        account_move_line_ids = self.env['account.move.line'].search([('account_id','=',datos['cuenta_id'][0]), ('date','<',datos['fecha_inicio'])], order='date')
        saldo = 0
        if account_move_line_ids:
            for movimiento in account_move_line_ids:
                saldo += movimiento.debit - movimiento.credit
        logging.warn(saldo)
        return saldo

    def movimientos(self, datos):
        moves = []
        account_move_line_ids = self.env['account.move.line'].search([('account_id','=',datos['cuenta_id'][0]), ('date','>=',datos['fecha_inicio']), ('date','<=',datos['fecha_fin'])], order='date')
        for movimiento in account_move_line_ids:

            mov = {
                'fecha': movimiento.date,
                # 'documento': movimiento.move_id.name if movimiento.move_id else '',
                'nombre': movimiento.partner_id.name if movimiento.partner_id else '',
                'descripcion': (movimiento.ref if movimiento.ref else ''),
                'debito': movimiento.debit,
                'credito': movimiento.credit,
                'saldo': 0,
                # 'moneda': linea.company_id.currency_id,
            }
            moves.append(mov)

        saldo_inicial = self.saldo_inicial(datos)
        saldo = saldo_inicial
        for m in moves:
            saldo = saldo + m['debito'] - m['credito']
            m['saldo'] = saldo

        logging.warn(moves)
        return moves



    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        logging.warn(data)
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'movimientos': self.movimientos,
            'saldo_inicial': self.saldo_inicial,
            # 'direccion': diario.direccion and diario.direccion.street,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
