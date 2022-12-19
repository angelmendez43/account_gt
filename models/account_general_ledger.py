# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta
import logging

class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"

    @api.model
    def _get_columns_name(self, options):
        res = super(AccountGeneralLedgerReport, self)._get_columns_name(options)
        for c in res:
            logging.warning('C NAME')
            logging.warning(c['name'])
            if c['name'] == '':
                c['name'] = 'Cuenta'
            if c['name'] == 'Comunicación':
                c['name'] = 'Descripción'
            if c['name'] == 'Balance':
                c['name'] = 'Saldo Final'
            if c['name'] == 'Crédito':
                c['name'] = 'Haber'
        return res
