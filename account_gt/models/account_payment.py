from odoo import api, fields, models, tools, _
from odoo.modules import get_module_resource


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    liquidacion_id = fields.Many2one('account_gt.liquidacion','Liquidacion')
