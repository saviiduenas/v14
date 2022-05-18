# -*- coding: utf-8 -*-

from odoo import api, models, fields
import re
import logging
from datetime import date
import datetime

class ReporteTicket(models.AbstractModel):
    _name = 'report.digifactfel.reporte_ticket'

    nombre_reporte = ''

    def fecha_hora_factura(self, fecha):
        fecha_convertida = datetime.datetime.strptime(str(fecha), '%Y-%m-%d').date().strftime('%Y-%m-%d')
        hora = datetime.datetime.strftime(fields.Datetime.context_timestamp(self, datetime.datetime.now()), "%H:%M:%S")
        fecha_hora_emision = str(fecha_convertida)+' '+str(hora)
        return fecha_hora_emision

    @api.model
    def _get_report_values(self, docids, data=None):
        model = 'account.move'
        docs = self.env['account.move'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'fecha_hora_factura': self.fecha_hora_factura,
            # 'movimientos': self.movimientos,
            # 'fecha_actual': self.fecha_actual,
        }
