# -*- encoding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
import logging

class LibroVentas(models.AbstractModel):
    _name = 'report.account_gt.reporte_libro_ventas'


    # def _get_ventas(self,datos):
    #     ventas_lista = []
    #     venta_ids = self.env['account.move'].search([('date','<=',datos['fecha_fin']),('date','>=',datos['fecha_inicio']),('state','=','posted'),('type','in',['out_invoice','out_refund'])])
    #     total = {'venta':0,'servicio':0,'exportacion':0,'iva':0,'total':0}
    #     documentos_operados = 0
    #     if venta_ids:
    #         for venta in venta_ids:
    #             documentos_operados += 1
    #             dic = {
    #                 'id': venta.id,
    #                 'fecha': venta.date,
    #                 'documento': venta.ref if venta.ref else venta.name,
    #                 'cliente': venta.partner_id.name if venta.partner_id else '',
    #                 'nit': venta.partner_id.vat if venta.partner_id.vat else '',
    #                 'venta': 0,
    #                 'servicio': 0,
    #                 'exportacion': 0,
    #                 'iva': venta.amount_by_group[0][1],
    #                 'total': venta.amount_total
    #             }
    #             for linea in venta.invoice_line_ids:
    #                 if venta.tipo_factura == 'varios':
    #                     if linea.product_id.type == 'product':
    #                         dic['venta'] = linea.price_subtotal
    #                     if linea.product_id.type != 'product':
    #                         dic['servicio'] =  linea.price_subtotal
    #                 else:
    #                     if venta.tipo_factura == 'venta':
    #                         dic['venta'] = linea.price_subtotal
    #                     if venta.tipo_factura == 'servicio':
    #                         dic['servicio'] = linea.price_subtotal
    #                     if venta.tipo_factura == 'exportacion':
    #                         dic['exportacion'] = linea.price_subtotal
    #
    #                 total['venta'] += dic['venta']
    #                 total['servicio'] += dic['servicio']
    #                 total['exportacion'] += dic['exportacion']
    #                 total['iva'] += dic['iva']
    #                 total['total'] += dic['total']
    #
    #             ventas_lista.append(dic)
    #     logging.warn(ventas_lista)
    #     return {'ventas_lista': ventas_lista,'total': total, 'documentos_operados': documentos_operados}


    def _get_conversion(self,move_id):
        conversion = {'impuesto': 0,'total':0 }
        total_sin_impuesto = 0
        total_total = 0


        amount_untaxed = 0
        amount_tax = 0
        amount_total = 0
        amount_residual = 0
        amount_untaxed_signed = 0
        amount_tax_signed = 0
        amount_total_signed = 0
        amount_residual_signed = 0


        for move in move_id:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.move_type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1

            # logging.warn(total_sin_impuesto)
            # logging.warn(total)




            amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            amount_total = sign * (total_currency if len(currencies) == 1 else total)
            amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            amount_untaxed_signed = -total_untaxed
            amount_tax_signed = -total_tax
            amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            amount_residual_signed = total_residual

            # logging.warn(move.name)
            logging.warn(amount_untaxed)
            logging.warn(amount_tax)
            logging.warn(amount_total)
            logging.warn(amount_residual)
            logging.warn(amount_untaxed_signed)
            logging.warn(amount_total_signed)
            logging.warn(amount_residual_signed)


            # total_sin_impuesto = -total_untaxed
            # total_total = sign * (total_currency if len(currencies) == 1 else total)
            if amount_residual_signed < 0:
                logging.warn('IF')
                logging.warn(amount_residual_signed)
                logging.warn(amount_tax_signed)
                conversion['impuesto'] = (amount_tax_signed *-1)
                conversion['total'] = amount_residual_signed * -1
            else:
                conversion['impuesto'] = (amount_tax_signed)
                conversion['total'] = amount_residual_signed
            logging.warn(move.name)
            logging.warn(conversion)

        return conversion
            # currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            # is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            # if move.move_type == 'entry':
            #     move.invoice_payment_state = False
            # elif move.state == 'posted' and is_paid:
            #     if move.id in in_payment_set:
            #         move.invoice_payment_state = 'in_payment'
            #     else:
            #         move.invoice_payment_state = 'paid'
            # else:
            #     move.invoice_payment_state = 'not_paid'


    def _get_impuesto_iva(self,tax_ids):
        impuesto_iva = False
        if len(tax_ids) > 0:
            for linea in tax_ids:
                if 'IVA' in linea.name:
                    impuesto_iva = True
                    logging.warn('si hay iva')
        return impuesto_iva

    def _get_ventas(self,datos):
        compras_lista = []
        gastos_no_lista = []
        logging.warn(self.env.company)
        compra_ids = self.env['account.move'].search([('company_id','=',self.env.company.id),('invoice_date','<=',datos['fecha_fin']),('invoice_date','>=',datos['fecha_inicio']),('state','=','posted'),
        ('move_type','in',['out_invoice','out_refund'])],order='invoice_date asc')

        total = {'compra':0,'compra_exento':0,'servicio':0,'servicio_exento':0,'importacion':0,'pequenio':0,'iva':0,'total':0,'reten_iva': 0}
        logging.warn(compra_ids)
        total_gastos_no = 0
        documentos_operados = 0
        if compra_ids:

                for compra in compra_ids:
                    if 'RECIB' not in compra.journal_id.code:
                        # logging.warn('TIPO CAMBIO')
                        # logging.warn(self._get_conversion(compra))

                        documentos_operados += 1
                        dic = {
                            'id': compra.id,
                            'fecha': compra.date,
                            'documento': compra.ref if compra.ref else compra.name,
                            'proveedor': compra.partner_id.name if compra.partner_id else '',
                            'nit': compra.partner_id.vat if compra.partner_id.vat else '',
                            'compra': 0,
                            'compra_exento':0,
                            'servicio': 0,
                            'servicio_exento': 0,
                            'importacion': 0,
                            'pequenio': 0,
                            'iva': 0,
                            'bruto': 0,
                            'total': 0,
                            'reten_iva': 0,
                            'correlativo_interno': compra.id,
                            'pais_destino': compra.company_id.country_id.name,
                            'observaciones': compra.name,
                        }
                        # if compra.currency_id.id != compra.company_id.currency_id.id:
                            # if len(compra.amount_by_group) > 0:
                            #     monto_convertir_iva = compra.currency_id.with_context(date=compra.invoice_date).compute(compra.amount_by_group[0][1], compra.company_id.currency_id)
                            #     monto_convertir_total = compra.currency_id.with_context(date=compra.invoice_date).compute(compra.amount_total, compra.company_id.currency_id)
                            #
                            #     dic['iva'] = 0.00
                            #     dic['total'] = self._get_conversion(compra)['total']
                            # else:
                            #     monto_convertir_total = compra.currency_id.with_context(date=compra.invoice_date).compute(compra.amount_total, compra.company_id.currency_id)
                            #     dic['iva'] = 0.00
                            #     dic['total'] = self._get_conversion(compra)['total']

                        reten_iva = self.env['account.move'].search([('ref','=', str(compra.name))])
                        if reten_iva:
                            for linea in reten_iva.line_ids:
                                logging.warn(linea.account_id.user_type_id.name)
                                if linea.account_id.user_type_id.name == 'Activos Circulantes':
                                    dic['reten_iva'] += linea.debit
                                    total['reten_iva'] += linea.debit

                        for linea in compra.invoice_line_ids:
                            impuesto_iva = False
                            impuesto_iva = self._get_impuesto_iva(linea.tax_ids)
                            if compra.currency_id.id != compra.company_id.currency_id.id:
                                if ((linea.product_id) and (('COMISION POR SERVICIOS' not in linea.product_id.name) or ('COMISIONES BANCARIAS' not in linea.product_id.name) or ('Servicios y Comisiones' not in linea.product_id.name))):
                                    if len(linea.tax_ids) > 0:
                                        monto_convertir_precio = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_unit, compra.company_id.currency_id)

                                        r = linea.tax_ids.compute_all(monto_convertir_precio, currency=compra.currency_id, quantity=linea.quantity, product=linea.product_id, partner=compra.partner_id)

                                        for i in r['taxes']:
                                            if 'IVA' in i['name']:
                                                dic['iva'] += i['amount']
                                            logging.warn(i)

                                        monto_convertir = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_subtotal, compra.company_id.currency_id)

                                        if compra.tipo_factura == 'varios':
                                            if linea.product_id.type == 'product':
                                                dic['compra'] += monto_convertir
                                            if linea.product_id.type != 'product':
                                                dic['servicio'] +=  monto_convertir
                                        elif compra.tipo_factura == 'exportacion' or self.env.company.id != compra.currency_id.id :
                                            dic['importacion'] += monto_convertir

                                        else:
                                            if linea.product_id.type == 'product':
                                                dic['compra'] += monto_convertir
                                            if linea.product_id.type != 'product':
                                                dic['servicio'] +=  monto_convertir



                                        if compra.partner_id.pequenio_contribuyente:
                                            dic['compra'] = 0
                                            dic['servicio'] = 0
                                            dic['importacion'] = 0
                                            dic['pequenio'] += monto_convertir

                                        # dic['total']
                                    else:
                                        monto_convertir = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_total, compra.company_id.currency_id)

                                        if compra.tipo_factura == 'varios':
                                            if linea.product_id.type == 'product':
                                                dic['compra'] += monto_convertir
                                            if linea.product_id.type != 'product':
                                                dic['servicio'] +=  monto_convertir
                                        elif compra.tipo_factura == 'exportacion' or self.env.company.id != compra.currency_id.id:
                                            dic['importacion'] += monto_convertir

                                        else:
                                            if linea.product_id.type == 'product':
                                                dic['compra_exento'] += monto_convertir
                                            if linea.product_id.type != 'product':
                                                dic['servicio_exento'] +=  monto_convertir



                                        if compra.partner_id.pequenio_contribuyente:
                                            dic['compra'] = 0
                                            dic['servicio'] = 0
                                            dic['importacion'] = 0
                                            dic['compra_exento'] = 0
                                            dic['servicio_exento'] = 0
                                            dic['pequenio'] += monto_convertir

                            else:
                                logging.warn(linea.product_id.name)
                                if ((linea.product_id) and (('COMISION POR SERVICIOS' not in linea.product_id.name) or ('COMISIONES BANCARIAS' not in linea.product_id.name) or ('Servicios y Comisiones' not in linea.product_id.name))):
                                    if len(linea.tax_ids) > 0:
                                        # monto_convertir_precio = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_unit, compra.company_id.currency_id)

                                        r = linea.tax_ids.compute_all(linea.price_unit, currency=compra.currency_id, quantity=linea.quantity, product=linea.product_id, partner=compra.partner_id)

                                        for i in r['taxes']:
                                            if 'IVA' in i['name']:
                                                dic['iva'] += i['amount']
                                            logging.warn(i)

                                        if compra.tipo_factura == 'varios':
                                            if linea.product_id.type == 'product':
                                                dic['compra'] += linea.price_subtotal
                                            if linea.product_id.type != 'product':
                                                dic['servicio'] +=  linea.price_subtotal
                                        elif compra.tipo_factura == 'importacion':
                                            dic['importacion'] += linea.price_subtotal
                                        else:
                                            if linea.product_id.type == 'product':
                                                dic['compra'] += linea.price_subtotal
                                            if linea.product_id.type != 'product':
                                                dic['servicio'] +=  linea.price_subtotal


                                        if compra.partner_id.pequenio_contribuyente:
                                            dic['compra'] = 0
                                            dic['servicio'] = 0
                                            dic['importacion'] = 0
                                            dic['compra_exento'] = 0
                                            dic['servicio_exento'] = 0
                                            dic['pequenio'] += linea.price_total


                                    else:
                                        if linea.product_id.type == 'product':
                                            dic['compra_exento'] += linea.price_total
                                        if linea.product_id.type != 'product':
                                            dic['servicio_exento'] +=  linea.price_total


                                        if compra.partner_id.pequenio_contribuyente:
                                            dic['compra'] = 0
                                            dic['servicio'] = 0
                                            dic['importacion'] = 0
                                            dic['compra_exento'] = 0
                                            dic['servicio_exento'] = 0
                                            dic['pequenio'] += linea.price_total


                                # dic['total'] = dic['compra'] + dic['servicio'] + dic['compra_exento'] + dic['servicio_exento'] + dic['importacion'] + dic['iva'] + dic['pequenio']
                                        # if i['id'] == datos['impuesto_id'][0]:
                                        #     linea['iva'] += i['amount']
                                        #     totales[tipo_linea]['iva'] += i['amount']
                                        #     totales[tipo_linea]['total'] += i['amount']
                                        # elif i['amount'] > 0:
                                        #     linea[f.tipo_gasto+'_exento'] += i['amount']
                                        #     totales[tipo_linea]['exento'] += i['amount']
                                        #






                            #
                            #     if impuesto_iva:
                            #     # if len(linea.tax_ids) > 0:
                            #         monto_convertir = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_subtotal, compra.company_id.currency_id)
                            #     #
                            #     #     if compra.tipo_factura == 'varios':
                            #     #         if linea.product_id.type == 'product':
                            #     #             dic['compra'] = monto_convertir
                            #     #         if linea.product_id.type != 'product':
                            #     #             dic['servicio'] =  monto_convertir
                            #     #     else:
                            #     #         if compra.tipo_factura == 'compra':
                            #     #             dic['compra'] = monto_convertir
                            #     #         if compra.tipo_factura == 'servicio':
                            #     #             dic['servicio'] = monto_convertir
                            #     #         if compra.tipo_factura == 'importacion':
                            #     #             dic['importacion'] = monto_convertir
                            #         monto_convertir_iva = compra.currency_id.with_context(date=compra.invoice_date).compute(compra.amount_by_group[0][1], compra.company_id.currency_id)
                            #         dic['iva'] += monto_convertir_iva
                            #         if compra.tipo_factura == 'varios':
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra'] += monto_convertir
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio']+ =  monto_convertir
                            #         elif compra.tipo_factura == 'importacion':
                            #             dic['importacion'] += monto_convertir:
                            #
                            #         else:
                            #             # if compra.tipo_factura == 'compra':
                            #             #     dic['compra'] = monto_convertir
                            #             # if compra.tipo_factura == 'servicio':
                            #             #     dic['servicio'] = monto_convertir
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra'] += monto_convertir
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio'] +=  monto_convertir
                            #     else:
                            #         dic['iva'] = 0
                            #         monto_convertir = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_total, compra.company_id.currency_id)
                            #         if compra.tipo_factura == 'varios':
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra_exento'] += monto_convertir
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio_exento'] +=  monto_convertir
                            #         elif compra.tipo_factura == 'importacion':
                            #             dic['importacion'] += monto_convertir
                            #         else:
                            #             # if compra.tipo_factura == 'compra':
                            #             #     logging.warn('COMPRA')
                            #             #     logging.warn(monto_convertir)
                            #             #     dic['compra_exento'] = monto_convertir
                            #             # if compra.tipo_factura == 'servicio':
                            #             #     dic['servicio_exento'] = monto_convertir
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra_exento'] = monto_convertir
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio_exento'] =  monto_convertir
                            #
                            #     total['servicio_exento'] += dic['servicio_exento']
                            #     total['compra_exento'] += dic['compra_exento']
                            #     total['importacion'] += dic['importacion']
                            #
                            # else:
                            #     if impuesto_iva:
                            #         if compra.tipo_factura == 'varios':
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra'] += linea.price_subtotal
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio'] +=  linea.price_subtotal
                            #         elif compra.tipo_factura == 'importacion':
                            #                 dic['importacion'] += linea.price_subtotal
                            #         else:
                            #             # if compra.tipo_factura == 'compra':
                            #             #     dic['compra'] = linea.price_subtotal
                            #             # if compra.tipo_factura == 'servicio':
                            #             #     dic['servicio'] = linea.price_subtotal
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra'] += linea.price_subtotal
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio'] +=  linea.price_subtotal
                            #         dic['iva'] += linea.
                            #     else:
                            #         if compra.tipo_factura == 'varios':
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra'] += linea.price_subtotal
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio'] +=  linea.price_subtotal
                            #         elif compra.tipo_factura == 'importacion':
                            #                 dic['importacion'] += linea.price_subtotal
                            #         else:
                            #             # if compra.tipo_factura == 'compra':
                            #             #     dic['compra'] = linea.price_subtotal
                            #             # if compra.tipo_factura == 'servicio':
                            #             #     dic['servicio'] = linea.price_subtotal
                            #             if linea.product_id.type == 'product':
                            #                 dic['compra'] += linea.price_subtotal
                            #             if linea.product_id.type != 'product':
                            #                 dic['servicio'] +=  linea.price_subtotal

                            # total['compra'] += dic['compra']
                            # total['compra_exento'] += dic['compra_exento']
                            # total['servicio'] += dic['servicio']
                            # total['servicio_exento'] += dic['servicio_exento']
                            # total['importacion'] += dic['importacion']
                            # total['pequenio'] += dic['pequenio']
                            # total['iva'] += dic['iva']
                            # total['total'] += dic['total']
                        dic['total'] = dic['compra'] + dic['servicio'] + dic['compra_exento'] + dic['servicio_exento'] + dic['importacion'] + dic['iva'] + dic['pequenio']

                        if compra.move_type in ['in_refund']:
                            # dic['total'] = dic['compra'] - dic['servicio'] - dic['compra_exento'] - dic['servicio_exento'] - dic['importacion'] - dic['iva'] - dic['pequenio']

                            dic['compra']  = dic['compra'] * -1
                            dic['compra_exento'] = dic['compra_exento'] * -1
                            dic['servicio'] =  dic['servicio'] * -1
                            dic['servicio_exento'] = dic['servicio_exento'] * -1
                            dic['importacion'] = dic['importacion'] * -1
                            dic['pequenio'] = dic['pequenio'] * -1
                            dic['iva'] = dic['iva'] * -1
                            dic['total'] = dic['total'] * -1
                            # total['compra'] -= dic['compra']
                            # total['compra_exento'] -= dic['compra_exento']
                            # total['servicio'] -= dic['servicio']
                            # total['servicio_exento'] -= dic['servicio_exento']
                            # total['importacion'] -= dic['importacion']
                            # total['pequenio'] -= dic['pequenio']
                            # total['iva'] -= dic['iva']
                            # total['total'] -= dic['total']


                            # total['compra'] += dic['compra']
                            # total['compra_exento'] += dic['compra_exento']
                            # total['servicio'] += dic['servicio']
                            # total['servicio_exento'] += dic['servicio_exento']
                            # total['importacion'] += dic['importacion']
                            # total['pequenio'] += dic['pequenio']
                            # total['iva'] += dic['iva']
                            # total['total'] += dic['total']
                        else:
                            # dic['total'] = dic['compra'] + dic['servicio'] + dic['compra_exento'] + dic['servicio_exento'] + dic['importacion'] + dic['iva'] + dic['pequenio']

                            total['compra'] += dic['compra']
                            total['compra_exento'] += dic['compra_exento']
                            total['servicio'] += dic['servicio']
                            total['servicio_exento'] += dic['servicio_exento']
                            total['importacion'] += dic['importacion']
                            total['pequenio'] += dic['pequenio']
                            total['iva'] += dic['iva']
                            total['total'] += dic['total']
                        compras_lista.append(dic)
                    else:
                        # GASTOS NO DEDUCIBLES
                        dic = {
                            'id': compra.id,
                            'fecha': compra.date,
                            'documento': compra.name,
                            'proveedor': compra.partner_id.name if compra.partner_id else '',
                            'nit': compra.partner_id.vat if compra.partner_id.vat else '',
                            'total': compra.amount_total
                        }
                        total_gastos_no += compra.amount_total
                        gastos_no_lista.append(dic)

        # logging.warn(compras_lista)
        return {'compras_lista': compras_lista,'total': total,'documentos_operados':documentos_operados,'gastos_no': gastos_no_lista,'total_gastos_no': total_gastos_no}

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        # if len(data['form']['diarios_id']) == 0:
        #     raise UserError("Por favor ingrese al menos un diario.")

        # diario = self.env['account.journal'].browse(data['form']['diarios_id'][0])

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            '_get_ventas': self._get_ventas,
            # 'lineas': self.lineas,
            # 'direccion': diario.direccion and diario.direccion.street,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
