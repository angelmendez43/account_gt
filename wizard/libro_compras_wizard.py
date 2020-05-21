# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibroComprasWizard(models.TransientModel):
    _name = 'account_gt.libro_compras.wizard'
    _description = "Wizard para libro de compras"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'account_gt.libro_compras.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_libro_compras').report_action([], data=data)
