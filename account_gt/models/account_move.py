from odoo import api, fields, models, tools, _
from odoo.modules import get_module_resource
from odoo.release import version_info
import logging

class AccountMove(models.Model):
    _inherit = 'account.move'

    if version_info[0] == 13:
        @api.onchange('journal_id')
        def onchange_tipo_factura(self):
            tipo = False
            if self.type in ['in_invoice','in_refund']:
                tipo = 'compra'
            if self.type in ['out_invoice','out_refund']:
                tipo = 'venta'
            logging.warn(tipo)
            self.tipo_factura = tipo
    else:
        @api.onchange('journal_id')
        def onchange_tipo_factura(self):
            tipo = False
            if self.move_type in ['in_invoice','in_refund']:
                tipo = 'compra'
            if self.move_type in ['out_invoice','out_refund']:
                tipo = 'venta'
            logging.warn(tipo)
            self.tipo_factura = tipo

    liquidacion_id = fields.Many2one('account_gt.liquidacion','Liquidacion')
    tipo_factura = fields.Selection([('venta','Venta'),('compra', 'Compra o Bien'), ('servicio', 'Servicio'),('varios','Varios'), ('combustible', 'Combustible'),('importacion', 'Importación'),('exportacion','Exportación')],
        string="Tipo de factura")

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    conciliacion_bancaria = fields.Boolean("Conciliacion bancaria")
    fecha_conciliacion_bancaria = fields.Date("Fecha conciliacion")
