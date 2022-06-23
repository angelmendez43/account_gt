# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlsxwriter
import base64
import io
import logging
from datetime import datetime
import datetime

class RecuperacionPagosWizard(models.TransientModel):
    _name = 'account_gt.recuperacion_pagos.wizard'
    _description = "Wizard para reporte de recuperacion de pagos"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'account_gt.recuperacion_pagos.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_recuperacion_pagos').report_action([], data=data)


    def print_report_excel(self):
        for w in self:
            dict = {}
            dict['fecha_inicio'] = w.fecha_inicio
            dict['fecha_fin'] = w.fecha_fin

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Recuperación de pagos')

            hoja.write(1, 0, 'Fecha recuperación')
            hoja.write(1, 1, 'Correlativo pago')
            hoja.write(1, 2, 'Diario')
            hoja.write(1, 3, 'Descripción')
            hoja.write(1, 4, 'Monto')
            hoja.write(1, 5, 'Forma de pago')
            hoja.write(1, 6, 'Usuario que recupero')
            hoja.write(1, 7, 'Correlativo factura')
            hoja.write(1, 8, 'Fecha factura')
            hoja.write(1, 9, 'Cliente')
            hoja.write(1, 10, 'NIT')
            hoja.write(1, 11, 'Sucursal')
            hoja.write(1, 12, 'Días de recuperación')
            hoja.write(1, 13, 'Porcentajes de recuperación')

            pagos = self.env['account.payment'].search([('date', '>=', w.fecha_inicio), ('date', '<=', w.fecha_fin), ('payment_type', '=', 'inbound')])

            fila=2
            for pago in pagos:
                fecha_pago = pago.date.strftime('%d/%m/%Y')
                hoja.write(fila, 0, fecha_pago)
                hoja.write(fila, 1, pago.name)
                hoja.write(fila, 2, pago.journal_id.name)
                if pago.descripcion:
                    hoja.write(fila, 3, pago.descripcion)
                hoja.write(fila, 4, pago.amount)
                if pago.reconciled_invoices_count:
                    fel_serie_fel_numero = ''
                    for factura in pago.reconciled_invoice_ids:
                        # logging.warning('Que es factura?')
                        # logging.warning(factura)
                        if factura.fel_serie and factura.fel_numero:
                            fel_serie_fel_numero = str(factura.fel_serie)+'-'+str(factura.fel_numero)
                        fecha_factura = factura.invoice_date.strftime('%d/%m/%Y')
                        hoja.write(fila, 7, fel_serie_fel_numero)
                        hoja.write(fila, 8, fecha_factura)
                        hoja.write(fila, 9, factura.partner_id.name)
                        hoja.write(fila, 10, factura.partner_id.vat)
                        hoja.write(fila, 11, factura.journal_id.name)
                        dias_recuperacion = pago.date - factura.invoice_date
                        # logging.warning('Cuantos días?')
                        # logging.warning("Que pago es?"+'   '+pago.name+' '+str(pago.date))
                        # logging.warning("Que factura es?"+'   '+factura.name+' '+str(factura.invoice_date))
                        # logging.warning(dias_recuperacion)
                        hoja.write(fila, 12, dias_recuperacion)
                fila+=1
            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'Recuperacion_pagos.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account_gt.recuperacion_pagos.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
