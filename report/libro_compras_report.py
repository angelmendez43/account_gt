# -*- encoding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
import logging

class LibroCompras(models.AbstractModel):
    _name = 'report.account_gt.reporte_libro_compras'


    def _get_compras(self,datos):
        compras_lista = []
        compra_ids = self.env['account.move'].search([('date','<=',datos['fecha_fin']),('date','>=',datos['fecha_inicio']),('state','=','posted'),('type','in',['in_invoice','in_refund'])])
        total = {'compra':0,'servicio':0,'importacion':0,'iva':0,'total':0}
        documentos_operados = 0
        if compra_ids:
            for compra in compra_ids:
                documentos_operados += 1
                dic = {
                    'id': compra.id,
                    'fecha': compra.date,
                    'documento': compra.ref if compra.ref else compra.name,
                    'proveedor': compra.partner_id.name if compra.partner_id else '',
                    'nit': compra.partner_id.vat if compra.partner_id.vat else '',
                    'compra': 0,
                    'servicio': 0,
                    'importacion': 0,
                    'iva': compra.amount_by_group[0][1],
                    'total': compra.amount_total
                }
                for linea in compra.invoice_line_ids:
                    if compra.tipo_factura == 'varios':
                        if linea.product_id.type == 'product':
                            dic['compra'] = linea.price_subtotal
                        if linea.product_id.type != 'product':
                            dic['servicio'] =  linea.price_subtotal
                    else:
                        if compra.tipo_factura == 'compra':
                            dic['compra'] = linea.price_subtotal
                        if compra.tipo_factura == 'servicio':
                            dic['servicio'] = linea.price_subtotal
                        if compra.tipo_factura == 'importacion':
                            dic['importacion'] = linea.price_subtotal

                    total['compra'] += dic['compra']
                    total['servicio'] += dic['servicio']
                    total['importacion'] += dic['importacion']
                    total['iva'] += dic['iva']
                    total['total'] += dic['total']
                compras_lista.append(dic)
        logging.warn(compras_lista)
        return {'compras_lista': compras_lista,'total': total,'documentos_operados':documentos_operados}

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
            '_get_compras': self._get_compras,
            # 'lineas': self.lineas,
            # 'direccion': diario.direccion and diario.direccion.street,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
