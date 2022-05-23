# -*- encoding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
import logging

class LibroCompras(models.AbstractModel):
    _name = 'report.account_gt.reporte_libro_compras'


    def _get_conversion(self,move_id):
        conversion = {'impuesto': 0,'total':0 }
        total_sin_impuesto = 0
        total_total = 0


        amount_untaxed = 0
        amount_tax = 0
        amount_total = 0
        amount_residual = 0
        amount_untaxed_signed = 0
        amount_tax_signed = 0
        amount_total_signed = 0
        amount_residual_signed = 0


        for move in move_id:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.move_type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1


            amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            amount_total = sign * (total_currency if len(currencies) == 1 else total)
            amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            amount_untaxed_signed = -total_untaxed
            amount_tax_signed = -total_tax
            amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            amount_residual_signed = total_residual

            logging.warn(amount_untaxed)
            logging.warn(amount_tax)
            logging.warn(amount_total)
            logging.warn(amount_residual)
            logging.warn(amount_untaxed_signed)
            logging.warn(amount_total_signed)
            logging.warn(amount_residual_signed)


            if amount_residual_signed < 0:
                logging.warn('IF')
                logging.warn(amount_residual_signed)
                logging.warn(amount_tax_signed)
                conversion['impuesto'] = (amount_tax_signed *-1)
                conversion['total'] = amount_residual_signed * -1
            else:
                conversion['impuesto'] = (amount_tax_signed)
                conversion['total'] = amount_residual_signed
            logging.warn(move.name)
            logging.warn(conversion)

        return conversion


    def _get_impuesto_iva(self,tax_ids):
        impuesto_iva = False
        if len(tax_ids) > 0:
            for linea in tax_ids:
                if 'IVA' in linea.name:
                    impuesto_iva = True
                    logging.warning('si hay iva')
        return impuesto_iva

    def _get_compras(self,datos):
        compras_lista = []
        gastos_no_lista = []
        logging.warn(self.env.company)
        compra_ids = self.env['account.move'].search([('company_id','=',self.env.company.id),('date','<=',datos['fecha_fin']),('date','>=',datos['fecha_inicio']),('state','=','posted'),('move_type','in',['in_invoice','in_refund'])])
        total = {'compra':0,'compra_exento':0,'servicio':0,'servicio_exento':0,'importacion':0,'pequenio':0, 'combustible':0, 'activo':0,'iva':0,'total':0}
        total_gastos_no = 0
        documentos_operados = 0
        if compra_ids:

                for compra in compra_ids:
                    if 'RECIB' not in compra.journal_id.code:

                        documentos_operados += 1
                        dic = {
                            'id': compra.id,
                            'fecha': compra.date,
                            'documento': compra.ref if compra.ref else compra.name,
                            'proveedor': compra.partner_id.name if compra.partner_id else '',
                            'nit': compra.partner_id.vat if compra.partner_id.vat else '',
                            'compra': 0,
                            'compra_exento':0,
                            'servicio': 0,
                            'servicio_exento': 0,
                            'importacion': 0,
                            'pequenio': 0,
                            'combustible':0,
                            'activo':0,
                            'iva': 0,
                            'total': 0
                        }


                        if compra.tipo_factura == 'combustible':
                            dic['combustible']+=(compra.amount_untaxed_signed*-1)
                            iva = (compra.amount_total_signed*-1)+ compra.amount_untaxed_signed
                            dic['iva']+= iva

                        if compra.tipo_factura == 'activo':
                            dic['activo']+=(compra.amount_untaxed_signed*-1)
                            iva = (compra.amount_total_signed*-1)+ compra.amount_untaxed_signed
                            dic['iva']+= iva


                        if compra.tipo_factura != 'combustible':
                            for linea in compra.invoice_line_ids:
                                impuesto_iva = False
                                impuesto_iva = self._get_impuesto_iva(linea.tax_ids)
                                if compra.currency_id.id != compra.company_id.currency_id.id:
                                    if ((linea.product_id) and (('COMISION POR SERVICIOS' not in linea.product_id.name) or ('COMISIONES BANCARIAS' not in linea.product_id.name) or ('Servicios y Comisiones' not in linea.product_id.name))):
                                        if len(linea.tax_ids) > 0:

                                            monto_convertir_precio = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_unit, compra.company_id.currency_id)

                                            r = linea.tax_ids.compute_all(monto_convertir_precio, currency=compra.currency_id, quantity=linea.quantity, product=linea.product_id, partner=compra.partner_id)

                                            for i in r['taxes']:
                                                if 'IVA' in i['name']:
                                                    dic['iva'] += i['amount']
                                                logging.warning(i)

                                            monto_convertir = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_subtotal, compra.company_id.currency_id)

                                            if compra.tipo_factura == 'varios':
                                                if linea.product_id.type == 'product':
                                                    dic['compra'] += monto_convertir
                                                if linea.product_id.type != 'product':
                                                    dic['servicio'] +=  monto_convertir
                                            elif compra.tipo_factura == 'importacion':
                                                dic['importacion'] += monto_convertir

                                            else:
                                                if linea.product_id.type == 'product':
                                                    dic['compra'] += monto_convertir
                                                if linea.product_id.type != 'product':
                                                    dic['servicio'] +=  monto_convertir



                                            if compra.partner_id.pequenio_contribuyente:
                                                dic['compra'] = 0
                                                dic['servicio'] = 0
                                                dic['importacion'] = 0
                                                dic['pequenio'] += monto_convertir

                                            # dic['total']
                                        else:
                                            monto_convertir = compra.currency_id.with_context(date=compra.invoice_date).compute(linea.price_total, compra.company_id.currency_id)

                                            if compra.tipo_factura == 'varios':
                                                if linea.product_id.type == 'product':
                                                    dic['compra'] += monto_convertir
                                                if linea.product_id.type != 'product':
                                                    dic['servicio'] +=  monto_convertir
                                            elif compra.tipo_factura == 'importacion':
                                                dic['importacion'] += monto_convertir

                                            else:
                                                if linea.product_id.type == 'product':
                                                    dic['compra_exento'] += monto_convertir
                                                if linea.product_id.type != 'product':
                                                    dic['servicio_exento'] +=  monto_convertir



                                            if compra.partner_id.pequenio_contribuyente:
                                                dic['compra'] = 0
                                                dic['servicio'] = 0
                                                dic['importacion'] = 0
                                                dic['compra_exento'] = 0
                                                dic['servicio_exento'] = 0
                                                dic['pequenio'] += monto_convertir

                                else:
                                    if ((linea.product_id) and (('COMISION POR SERVICIOS' not in linea.product_id.name) or ('COMISIONES BANCARIAS' not in linea.product_id.name) or ('Servicios y Comisiones' not in linea.product_id.name))):
                                        if len(linea.tax_ids) > 0:

                                            r = linea.tax_ids.compute_all(linea.price_unit, currency=compra.currency_id, quantity=linea.quantity, product=linea.product_id, partner=compra.partner_id)

                                            for i in r['taxes']:
                                                if 'IVA' in i['name']:
                                                    dic['iva'] += i['amount']
                                                logging.warning(i)

                                            if compra.tipo_factura == 'varios':
                                                if linea.product_id.type == 'product':
                                                    dic['compra'] += linea.price_subtotal
                                                if linea.product_id.type != 'product':
                                                    dic['servicio'] +=  linea.price_subtotal
                                            elif compra.tipo_factura == 'importacion':
                                                dic['importacion'] += linea.price_subtotal
                                            else:
                                                if linea.product_id.type == 'product':
                                                    dic['compra'] += linea.price_subtotal
                                                if linea.product_id.type != 'product':
                                                    dic['servicio'] +=  linea.price_subtotal


                                            if compra.partner_id.pequenio_contribuyente:
                                                dic['compra'] = 0
                                                dic['servicio'] = 0
                                                dic['importacion'] = 0
                                                dic['compra_exento'] = 0
                                                dic['servicio_exento'] = 0
                                                dic['pequenio'] += linea.price_total


                                        else:
                                            if linea.product_id.type == 'product':
                                                dic['compra_exento'] += linea.price_total
                                            if linea.product_id.type != 'product':
                                                dic['servicio_exento'] +=  linea.price_total


                                            if compra.partner_id.pequenio_contribuyente:
                                                dic['compra'] = 0
                                                dic['servicio'] = 0
                                                dic['importacion'] = 0
                                                dic['compra_exento'] = 0
                                                dic['servicio_exento'] = 0
                                                dic['pequenio'] += linea.price_total


                        dic['total'] = dic['activo'] + dic['combustible'] + dic['compra'] + dic['servicio'] + dic['compra_exento'] + dic['servicio_exento'] + dic['importacion'] + dic['iva'] + dic['pequenio']

                        if compra.move_type in ['in_refund']:

                            dic['compra']  = dic['compra'] * -1
                            dic['compra_exento'] = dic['compra_exento'] * -1
                            dic['servicio'] =  dic['servicio'] * -1
                            dic['servicio_exento'] = dic['servicio_exento'] * -1
                            dic['importacion'] = dic['importacion'] * -1
                            dic['pequenio'] = dic['pequenio'] * -1
                            dic['iva'] = dic['iva'] * -1
                            dic['total'] = dic['total'] * -1

                        else:

                            total['compra'] += dic['compra']
                            total['compra_exento'] += dic['compra_exento']
                            total['servicio'] += dic['servicio']
                            total['servicio_exento'] += dic['servicio_exento']
                            total['importacion'] += dic['importacion']
                            total['pequenio'] += dic['pequenio']
                            total['combustible'] += dic['combustible']
                            total['activo'] += dic['activo']
                            total['iva'] += dic['iva']
                            total['total'] += dic['total']
                        compras_lista.append(dic)
                    else:
                        # GASTOS NO DEDUCIBLES
                        dic = {
                            'id': compra.id,
                            'fecha': compra.date,
                            'documento': compra.name,
                            'proveedor': compra.partner_id.name if compra.partner_id else '',
                            'nit': compra.partner_id.vat if compra.partner_id.vat else '',
                            'total': compra.amount_total
                        }
                        total_gastos_no += compra.amount_total
                        gastos_no_lista.append(dic)

        logging.warning("Recorriendo algo ")
        logging.warning(compras_lista)
        dicc_resumen_total={
            0:{
                'total_iva_combustible':0,
                'total_combustible':0
                },
            1:{
                'total_iva_compras':0,
                'total_compras':0
            },
            2:{
                'total_iva_servicio':0,
                'total_servicio':0
            },
            3:{
                'total_iva_pequenio':0,
                'total_pequenio':0
            },
            4:{
                'total_iva_importaciones':0,
                'total_importaciones':0
            },
            5:{
                'total_iva_vehiculos':0,
                'total_vehiculos':0
            },
            6:{
                'total_iva_exento':0,
                'total_exento':0
            }
        }

        for lista in compras_lista:
            total_combustible=0
            total_compras=0
            total_servicio=0
            for id_compra in lista:
                if id_compra == 'combustible':
                    if lista['combustible']>0:
                        dicc_resumen_total[0]['total_iva_combustible']+=lista['iva']
                        dicc_resumen_total[0]['total_combustible']+=lista['total']
                if id_compra == 'compra':
                    if lista['compra']>0:
                        dicc_resumen_total[1]['total_iva_compras']+=lista['iva']
                        dicc_resumen_total[1]['total_compras']+=lista['total']
                if id_compra == 'servicio':
                    if lista['servicio']>0:
                        dicc_resumen_total[2]['total_iva_servicio']+=lista['iva']
                        dicc_resumen_total[2]['total_servicio']+=lista['total']
                if id_compra == 'pequenio':
                    if lista['pequenio']>0:
                        dicc_resumen_total[3]['total_iva_pequenio']+=lista['iva']
                        dicc_resumen_total[3]['total_pequenio']+=lista['total']
                if id_compra == 'importacion':
                    if lista['importacion']>0:
                        dicc_resumen_total[4]['total_iva_importaciones']+=lista['iva']
                        dicc_resumen_total[4]['total_importaciones']+=lista['total']
                if id_compra == 'activo':
                    if lista['activo']>0:
                        dicc_resumen_total[5]['total_iva_vehiculos']+=lista['iva']
                        dicc_resumen_total[5]['total_vehiculos']+=lista['total']
                if id_compra == 'compra_exento':
                    if lista['compra_exento']>0:
                        dicc_resumen_total[6]['total_iva_exento']+=lista['iva']
                        dicc_resumen_total[6]['total_exento']+=lista['total']

        logging.warning('')
        logging.warning('')
        logging.warning(dicc_resumen_total)
        return {'compras_lista': compras_lista,'total': total,'documentos_operados':documentos_operados,'resumen_total':dicc_resumen_total,'gastos_no': gastos_no_lista,'total_gastos_no': total_gastos_no}

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            '_get_compras': self._get_compras,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
