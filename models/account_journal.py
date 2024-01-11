# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents
import logging
import re
import warnings

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    tipo_factura = fields.Selection([('FACT', 'FACT'),
    ('FCAM', 'FCAM'),
    ('FPEQ', 'FPEQ'),
    ('FCAP', 'FCAP'),
    ('FESP', 'FESP'),
    ('NABN', 'NABN'),
    ('RDON', 'RDON'),
    ('RECI', 'RECI'),
    ('NDEB', 'NDEB'),
    ('NCRE', 'NCRE'),
    ('DUCA', 'DUCA')], 'Tipo de Documento FEL', copy=False)
