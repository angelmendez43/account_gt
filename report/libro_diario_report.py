# -*- encoding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
import logging

class LibroDiario(models.AbstractModel):
    _name = 'report.account_gt.reporte_libro_diario'

    def inicio_libro_diario(self):
        logging.warning('Hello my friend')
        return True

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        logging.warning('Linea 18')
        logging.warn(data)
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
        }
