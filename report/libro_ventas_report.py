# -*- encoding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
import logging

class LibroVentas(models.AbstractModel):
    _name = 'report.account_gt.reporte_libro_ventas'


    def _get_ventas(self,datos):
        ventas_lista = []
        venta_ids = self.env['account.move'].search([('date','<=',datos['fecha_fin']),('date','>=',datos['fecha_inicio']),('state','=','posted'),('type','in',['out_invoice','out_refund'])])
        total = {'venta':0,'servicio':0,'exportacion':0,'iva':0,'total':0}
        documentos_operados = 0
        if venta_ids:
            for venta in venta_ids:
                documentos_operados += 1
                dic = {
                    'id': venta.id,
                    'fecha': venta.date,
                    'documento': venta.ref if venta.ref else venta.name,
                    'cliente': venta.partner_id.name if venta.partner_id else '',
                    'nit': venta.partner_id.vat if venta.partner_id.vat else '',
                    'venta': 0,
                    'servicio': 0,
                    'exportacion': 0,
                    'iva': venta.amount_by_group[0][1],
                    'total': venta.amount_total
                }
                for linea in venta.invoice_line_ids:
                    if venta.tipo_factura == 'varios':
                        if linea.product_id.type == 'product':
                            dic['venta'] = linea.price_subtotal
                        if linea.product_id.type != 'product':
                            dic['servicio'] =  linea.price_subtotal
                    else:
                        if venta.tipo_factura == 'venta':
                            dic['venta'] = linea.price_subtotal
                        if venta.tipo_factura == 'servicio':
                            dic['servicio'] = linea.price_subtotal
                        if venta.tipo_factura == 'exportacion':
                            dic['exportacion'] = linea.price_subtotal

                    total['venta'] += dic['venta']
                    total['servicio'] += dic['servicio']
                    total['exportacion'] += dic['exportacion']
                    total['iva'] += dic['iva']
                    total['total'] += dic['total']

                ventas_lista.append(dic)
        logging.warn(ventas_lista)
        return {'ventas_lista': ventas_lista,'total': total, 'documentos_operados': documentos_operados}

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        # if len(data['form']['diarios_id']) == 0:
        #     raise UserError("Por favor ingrese al menos un diario.")

        # diario = self.env['account.journal'].browse(data['form']['diarios_id'][0])

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            '_get_ventas': self._get_ventas,
            # 'lineas': self.lineas,
            # 'direccion': diario.direccion and diario.direccion.street,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
