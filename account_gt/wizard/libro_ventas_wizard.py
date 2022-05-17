# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlsxwriter
import base64
import io
import logging

class LibroVentasWizard(models.TransientModel):
    _name = 'account_gt.libro_ventas.wizard'
    _description = "Wizard para libro de ventas"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'account_gt.libro_ventas.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_libro_ventas').report_action([], data=data)

    def print_report_excel(self):
        for w in self:
            dict = {}
            dict['fecha_inicio'] = w.fecha_inicio
            dict['fecha_fin'] = w.fecha_fin
            # dict['impuesto_id'] = [w.impuesto_id.id, w.impuesto_id.name]
            # dict['diarios_id'] =[x.id for x in w.diarios_id]

            res = self.env['report.account_gt.reporte_libro_ventas']._get_ventas(dict)

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Reporte ventas')

            hoja.write(0, 0, 'LIBRO DE VENTAS Y SERVICIOS')
            hoja.write(2, 0, 'NUMERO DE IDENTIFICACION TRIBUTARIA')
            hoja.write(2, 1, self.env.company.vat)
            hoja.write(3, 0, 'NOMBRE COMERCIAL')
            hoja.write(3, 1,  self.env.company.name)
            hoja.write(2, 3, 'DOMICILIO FISCAL')
            hoja.write(2, 4,  self.env.company.street)
            hoja.write(3, 3, 'REGISTRO DEL')
            hoja.write(3, 4, str(w.fecha_inicio) + ' al ' + str(w.fecha_fin))



            hoja.write(5, 0, 'Fecha')
            hoja.write(5, 1, 'Documento')
            hoja.write(5, 2, 'NIT')
            hoja.write(5, 3, 'Cliente')
            hoja.write(5, 4, 'Bien')
            hoja.write(5, 5, 'Ventas exentas')
            hoja.write(5, 6, 'Servicios')
            hoja.write(5, 7, 'Servicios exentos')
            hoja.write(5, 8, 'Importacion')
            hoja.write(5, 9, 'IVA')
            hoja.write(5, 10, 'Bruto')
            hoja.write(5, 11, 'Reten IVA')
            hoja.write(5, 12, 'Correlativo interno')
            hoja.write(5, 13, 'País destino')
            hoja.write(5, 14, 'OBSERVACIONES')

            fila = 6
            for compra in res['compras_lista']:
                hoja.write(fila, 0, compra['fecha'])
                hoja.write(fila, 1, compra['documento'])
                hoja.write(fila, 2, compra['nit'])
                hoja.write(fila, 3, compra['proveedor'])
                hoja.write(fila, 4, compra['compra'])
                hoja.write(fila, 5, compra['compra_exento'])
                hoja.write(fila, 6, compra['servicio'])
                hoja.write(fila, 7, compra['servicio_exento'])
                hoja.write(fila, 8, compra['importacion'])
                hoja.write(fila, 9, compra['iva'])
                hoja.write(fila, 10, compra['total'])
                hoja.write(fila, 11, compra['reten_iva'])
                hoja.write(fila, 12, compra['correlativo_interno'])
                hoja.write(fila, 13, compra['pais_destino'])
                hoja.write(fila, 14, compra['observaciones'])


                fila += 1


            hoja.write(fila, 5, res['total']['compra'])
            hoja.write(fila, 6, res['total']['compra_exento'])
            hoja.write(fila, 7, res['total']['servicio'])
            hoja.write(fila, 8, res['total']['servicio_exento'])
            hoja.write(fila, 9, res['total']['importacion'])
            hoja.write(fila, 10, res['total']['iva'])
            hoja.write(fila, 12, res['total']['total'])
            hoja.write(fila, 11, res['total']['reten_iva'])

            fila += 1


            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'libro_ventas.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account_gt.libro_ventas.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
