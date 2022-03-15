# -*- coding: utf-8 -*-

import time
import math
import re

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    nit_digifactfel = fields.Char('Nit DIGIFACTFEL')
    feel_frase = fields.Char('Tipo de frase Feel')
    feel_frase_ids = fields.One2many('feel_digifact','company_id','Frases')
    feel_codigo_exportador = fields.Char('Codigo exportador')
    usuario_digifact = fields.Char('Usuario digifact')
    pass_digifact = fields.Char('Contraseña digifact')
    fel_prueba = fields.Boolean('Fel prueba')
    feel_codigo_exportador = fields.Char('Codigo exportador')
    certificador = fields.Char('Certificador', default="DIGIFACT")
    feel_logo = fields.Binary('Logo fel')
    feel_texto_logo = fields.Char('Texto logo fel')
    # feel_codigo_establecimiento = fields.Char('Codigo de establecimiento')
