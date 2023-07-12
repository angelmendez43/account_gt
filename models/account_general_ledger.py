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
        logging.warning(res)
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
        # res.insert(2, {'name': 'Serie'})
        # res.insert(3, {'name': 'Numero'})
        return res
    
    def _get_query_amls_select_clause(self):
        select_str = super(AccountGeneralLedgerReport, self)._get_query_amls_select_clause()
        select_str += '''
            ,account_payment.descripcion,
            move.fel_serie,
            move.fel_numero
        '''
        return select_str
        
        
    def _get_query_amls_from_clause(self):
        from_str = super(AccountGeneralLedgerReport, self)._get_query_amls_from_clause()
        from_str += """
            LEFT JOIN account_payment account_payment ON account_payment.id = account_move_line.payment_id \
        """
        return from_str
    
    @api.model
    def _get_aml_line(self, options, account, aml, cumulated_balance):
        res = super(AccountGeneralLedgerReport, self)._get_aml_line(options, account, aml, cumulated_balance)
        logging.warning('_get_aml_line')
        logging.warning(res)
        logging.warning(aml)
        if 'level' in res and res['level'] == 2:
            fel_serie = aml['fel_serie'] if aml['fel_serie'] else ""
            fel_numero = aml['fel_numero'] if aml['fel_numero'] else ""
            res['columns'].insert(1,  {'name': fel_serie, 'class': 'o_account_report_line_ellipsis'})
            res['columns'].insert(2,  {'name': fel_numero, 'class': 'o_account_report_line_ellipsis'})
            #res['columns'].insert(3,  {'name': "", 'class': 'o_account_report_line_ellipsis'})
        #if 'caret_options' in res and res['caret_options'] == 'account.payment':
        #    logging.warning('caret_options')
        #    res['columns'].insert(1,  {'name': '', 'class': 'o_account_report_line_ellipsis'})
        #    res['columns'].insert(2,  {'name': '', 'class': 'o_account_report_line_ellipsis'})
        if 'columns' in res and len(res['columns']) > 1:
            if aml['payment_id']:
                if 'name' in res['columns'][1] and res['columns'][1]['name'] and aml['descripcion']:
                    res['columns'][1]['name'] += ", "+ aml['descripcion']
                    #res['columns'].insert(1,  {'name': '', 'class': 'o_account_report_line_ellipsis'})
                    #res['columns'].insert(2,  {'name': '', 'class': 'o_account_report_line_ellipsis'})
            #else:
                #logging.warning('entra el res')
                #if aml['fel_serie']:
                    #logging.warning('si tiene fel_serie')
                    #res['columns'].insert(1,  {'name': aml['fel_serie'], 'class': 'o_account_report_line_ellipsis'})
                    #res['columns'].insert(2,  {'name': aml['fel_numero'], 'class': 'o_account_report_line_ellipsis'})
                    #logging.warning('despues de insertar')
                    #logging.warning(res)
        return res
