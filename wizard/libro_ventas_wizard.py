# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibroVentasWizard(models.TransientModel):
    _name = 'account_gt.libro_ventas.wizard'
    _description = "Wizard para libro de ventas"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'account_gt.libro_ventas.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_libro_ventas').report_action([], data=data)
