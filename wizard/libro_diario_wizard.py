# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlsxwriter
import base64
import io
import logging

class LibroDiarioWizard(models.TransientModel):
    _name ="account_gt.libro_diario.wizard"
    _description ="Wizard creado para libro diario"

    fecha_inicio = fields.Date('Fecha inicio: ')
    fecha_fin = fields.Date('Fecha final: ')
    name = fields.Char('Nombre archivo: ', size=32)
    archivo = fields.Binary('Archivo ', filters='.xls')

    def print_report(self):
        data = {
            'ids':[],
            'model': 'account_gt.libro_diario.wizard',
            'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_libro_diario').report_action([], data=data)


    def print_report_excel(self):
        logging.warning('Estamos funcionando bien :D')
        for w in self:
            dict = {}
            dict['fecha_inicio'] = w.fecha_inicio
            dict['fecha_fin'] = w.fecha_fin

            # res = self.env['report.account_gt.reporte_libro_diario']._get_ventas(dict)

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Reporte libro diario')

            hoja.write(0, 0, 'LIBRO DIARIO')

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'libro_diario.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account_gt.libro_diario.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
