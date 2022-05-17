# -*- encoding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
import logging

class LibroConciliacionBancaria(models.AbstractModel):
    _name = 'report.account_gt.reporte_libro_conciliacion_bancaria'


    def saldo_inicial(self, datos):
        account_move_line_ids = self.env['account.move.line'].search([('account_id','=',datos['cuenta_id'][0]), ('date','<',datos['fecha_inicio']),('conciliacion_bancaria','=',True)], order='date')
        saldo = 0
        if account_move_line_ids:
            for movimiento in account_move_line_ids:
                saldo += movimiento.debit - movimiento.credit
        logging.warn(saldo)
        return saldo

    def movimientos(self, datos):
        moves = []
        account_move_line_ids = self.env['account.move.line'].search([('account_id','=',datos['cuenta_id'][0]), ('date','>=',datos['fecha_inicio']), ('date','<=',datos['fecha_fin'])], order='date')
        return moves

    def documentos_conciliados(self,datos):
        documentos = []
        saldo_conciliado = 0
        account_move_line_ids = self.env['account.move.line'].search([('account_id','=',datos['cuenta_id'][0]), ('date','>=',datos['fecha_inicio']), ('date','<=',datos['fecha_fin']),('conciliacion_bancaria','=',True)], order='date')
        logging.warn(account_move_line_ids)
        if account_move_line_ids:
            for move in account_move_line_ids:
                movimiento = {
                    'fecha': move.date,
                    'documento': move.move_id.name if move.move_id else '',
                    'beneficiario': move.partner_id.name if move.partner_id else '',
                    'concepto': move.ref if move.ref else '',
                    'debito': move.debit,
                    'credito': move.credit,
                }
                saldo_conciliado += move.debit - move.credit
                documentos.append(movimiento)
        return {'documentos': documentos, 'saldo_conciliado': saldo_conciliado}


    def documentos_circulacion(self,datos):
        documentos = []
        account_move_line_ids = self.env['account.move.line'].search([('account_id','=',datos['cuenta_id'][0]), ('date','>=',datos['fecha_inicio']), ('date','<=',datos['fecha_fin']),('conciliacion_bancaria','=',False)], order='date')
        if account_move_line_ids:
            for move in account_move_line_ids:
                movimiento = {
                    'fecha': move.date,
                    'documento': move.move_id.name if move.move_id else '',
                    'beneficiario': move.partner_id.name if move.partner_id else '',
                    'concepto': move.ref if move.ref else '',
                    'debito': move.debit,
                    'credito': move.credit,
                }
                documentos.append(movimiento)
        return documentos

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
            'documentos_circulacion': self.documentos_circulacion,
            'documentos_conciliados': self.documentos_conciliados,
            # 'direccion': diario.direccion and diario.direccion.street,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
