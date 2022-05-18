# -*- coding: utf-8 -*-

import time
import math
import re

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    feel_tipo_dte = fields.Selection([
            ('FACT', 'Factura'),
            ('FCAM', 'Factura cambiaria'),
            ('FPEQ', 'Factura pequeño contribuyente'),
            ('FCAP', 'Factura cambiaria pequeño contribuyente'),
            ('FESP', 'Factura especial'),
            ('NABN','Nota de abono'),
            ('RDON','Recibo de donación'),
            ('RECI','Recibo'),
            ('NDEB','Nota de Débito'),
            ('NCRE','Nota de Crédito'),
            ('FACA','Factura Contribuyente Agropecuario'),
            ('FCCA','Factura Cambiaria Contribuyente Agropecuario'),
            ('FAPE','Factura Pequeño contribuyente Regimen Elctrónico'),
            ('FCPE','Factura Cambiaria Pequeño contribuyente Regimen Elctrónico'),
            ('FAAE','Factura Contribuyente Agropecuario Régimen Electrónico especial'),
            ('FCAE','Factura Cambiaria Contribuyente Agropecuario Régimen Electrónico especial'),
        ],string="Tipo DTE",
        help="Tipo de DTE (documento para feel)")
    feel_codigo_establecimiento = fields.Char('Codigo de establecimiento')
    feel_usuario = fields.Char('Usuario feel')
    feel_llave_pre_firma = fields.Char('Llave pre firma feel')
    feel_llave_firma = fields.Char('Llave firma feel')
    feel_nombre_comercial = fields.Char('Nombre comercial')
    producto_descripcion = fields.Boolean('Producto + descripcion')
    descripcion_factura = fields.Boolean('Descripcion factura')
    direccion_sucursal = fields.Char('Dirección')
    telefono = fields.Char('Teléfono')
