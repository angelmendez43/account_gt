# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlsxwriter
import base64
import io
import logging

class LibroComprasWizard(models.TransientModel):
    _name = 'account_gt.libro_compras.wizard'
    _description = "Wizard para libro de compras"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'account_gt.libro_compras.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('account_gt.action_libro_compras').report_action([], data=data)


    def print_report_excel(self):
        for w in self:
            dict = {}
            dict['fecha_inicio'] = w.fecha_inicio
            dict['fecha_fin'] = w.fecha_fin
            # dict['impuesto_id'] = [w.impuesto_id.id, w.impuesto_id.name]
            # dict['diarios_id'] =[x.id for x in w.diarios_id]

            res = self.env['report.account_gt.reporte_libro_compras']._get_compras(dict)

            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            hoja = libro.add_worksheet('Reporte compras')

            hoja.write(0, 0, 'LIBRO DE COMPRAS Y SERVICIOS')
            hoja.write(2, 0, 'NUMERO DE IDENTIFICACION TRIBUTARIA')
            hoja.write(2, 1, self.env.company.vat)
            hoja.write(3, 0, 'NOMBRE COMERCIAL')
            hoja.write(3, 1,  self.env.company.name)
            hoja.write(2, 3, 'DOMICILIO FISCAL')
            hoja.write(2, 4,  self.env.company.street)
            hoja.write(3, 3, 'REGISTRO DEL')
            hoja.write(3, 4, str(w.fecha_inicio) + ' al ' + str(w.fecha_fin))



            hoja.write(5, 0, 'Fecha')
            hoja.write(5, 1, 'Documento')
            hoja.write(5, 2, 'NIT')
            hoja.write(5, 3, 'Proveedor')
            hoja.write(5, 4, 'Combustible')
            hoja.write(5, 5, 'Compras')
            hoja.write(5, 6, 'Exentos')
            hoja.write(5, 7, 'Servicios')
            hoja.write(5, 8, 'Servicios exentos')
            hoja.write(5, 9, 'Importacion')
            hoja.write(5, 10, 'Pequeño contribuyente')
            hoja.write(5, 11, 'Activos')
            hoja.write(5, 12, 'IVA')
            hoja.write(5, 13, 'Total')

            fila = 6
            iva_proveedor=0
            iva_combustible=0
            iva_compra=0
            iva_servicios=0
            iva_pequenio=0
            iva_importaciones=0
            iva_exento=0
            iva_activo=0
            for compra in res['compras_lista']:
                hoja.write(fila, 0, compra['fecha'])
                hoja.write(fila, 1, compra['documento'])
                hoja.write(fila, 2, compra['nit'])
                hoja.write(fila, 3, compra['proveedor'])
                hoja.write(fila, 4, compra['combustible'])
                if compra['combustible']>0:
                    iva_combustible+=compra['iva']
                hoja.write(fila, 5, compra['compra'])
                if compra['compra']>0:
                    iva_compra+=compra['iva']
                hoja.write(fila, 6, compra['compra_exento'])
                if compra['compra_exento']>0:
                    iva_exento+=compra['iva']
                hoja.write(fila, 7, compra['servicio'])
                if compra['servicio']>0:
                    iva_servicios+=compra['iva']
                hoja.write(fila, 8, compra['servicio_exento'])
                hoja.write(fila, 9, compra['importacion'])
                if compra['importacion']>0:
                    iva_importaciones+=compra['iva']
                hoja.write(fila, 10, compra['pequenio'])
                if compra['pequenio']>0:
                    iva_pequenio+=compra['iva']
                hoja.write(fila,11, compra['activo'])
                if compra['activo']>0:
                    iva_activo+=compra['iva']

                hoja.write(fila, 12, compra['iva'])
                hoja.write(fila, 13, compra['total'])

                fila += 1


            hoja.write(fila, 4, res['total']['combustible'])
            hoja.write(fila, 5, res['total']['compra'])
            hoja.write(fila, 6, res['total']['compra_exento'])
            hoja.write(fila, 7, res['total']['servicio'])
            hoja.write(fila, 8, res['total']['servicio_exento'])
            hoja.write(fila, 9, res['total']['importacion'])
            hoja.write(fila, 10, res['total']['pequenio'])
            hoja.write(fila, 11, res['total']['activo'])
            hoja.write(fila, 12, res['total']['iva'])
            hoja.write(fila, 13, res['total']['total'])

            fila += 1


            hoja.write(fila, 12, 'Documentos operados:')
            hoja.write(fila, 13, res['documentos_operados'])

            fila += 1
            logging.warning(res['gastos_no'])
            if len(res['gastos_no']) > 0:

                hoja.write(fila,0,'Gastos no deducibles')

                fila += 1

                hoja.write(fila,0,'Fecha')
                hoja.write(fila,1,'Documento')
                hoja.write(fila,2,'NIT')
                hoja.write(fila,3,'Proveedor')
                hoja.write(fila,4,'Total')

                fila += 1

                for gasto in res['gastos_no']:
                    hoja.write(fila,0,gasto['fecha'])
                    hoja.write(fila,1,gasto['documento'])
                    hoja.write(fila,2,gasto['nit'])
                    hoja.write(fila,3,gasto['proveedor'])
                    hoja.write(fila,4,gasto['total'])

                    fila += 1


                hoja.write(fila,3,'Total gastos no deducibles')
                hoja.write(fila,4,res['total_gastos_no'])

            fila+=2
            hoja.write(fila,3,'Resumen')
            hoja.write(fila,4,'Base')
            hoja.write(fila,5,'IVA')
            hoja.write(fila,6,'Total')

            fila+=1
            hoja.write(fila,3,'Total de combustibles: ')
            hoja.write(fila,4,res['total']['combustible'])
            hoja.write(fila,5,iva_combustible)
            total_combustible=iva_combustible+res['total']['combustible']
            hoja.write(fila,6,total_combustible)
            fila+=1
            hoja.write(fila,3,'Total de compras: ')
            hoja.write(fila,4,res['total']['compra'])
            hoja.write(fila,5,iva_compra)
            total_compra=res['total']['compra']+iva_compra
            hoja.write(fila,6,total_compra)
            fila+=1
            hoja.write(fila,3,'Total de servicios: ')
            hoja.write(fila,4,res['total']['servicio'])
            hoja.write(fila,5,iva_servicios)
            total_servicios=res['total']['servicio']+iva_servicios
            hoja.write(fila,6,total_servicios)
            fila+=1
            hoja.write(fila,3,'Pequeños contribuyentes: ')
            hoja.write(fila,4,res['total']['pequenio'])
            hoja.write(fila,5,iva_pequenio)
            total_pequenio=res['total']['pequenio']+iva_pequenio
            hoja.write(fila,6,total_pequenio)
            fila+=1
            hoja.write(fila,3,'Total de importaciones: ')
            hoja.write(fila,4,res['total']['importacion'])
            hoja.write(fila,5,iva_importaciones)
            total_importaciones=res['total']['importacion']+iva_importaciones
            hoja.write(fila,6,total_importaciones)
            fila+=1
            hoja.write(fila,3,'Vehículos: ')
            hoja.write(fila,4,res['total']['activo'])
            hoja.write(fila,5,iva_activo)
            total_activo = res['total']['activo']+iva_activo
            hoja.write(fila,6,total_activo)

            fila+=1
            hoja.write(fila,3,'Total exento: ')
            hoja.write(fila,4,res['total']['compra_exento'])
            hoja.write(fila,5,iva_exento)
            total_exento=res['total']['compra_exento']+iva_exento
            hoja.write(fila,6,total_exento)



            fila+=1
            hoja.write(fila,3,'Total General: ')
            if res['total']['total'] > res['total']['iva']:
                base = res['total']['total']-res['total']['iva']
            hoja.write(fila,4, base)
            hoja.write(fila,5, res['total']['iva'])
            hoja.write(fila,6, res['total']['total'])
            fila+=1
            hoja.write(fila,3,'Total documentos operados: ')
            hoja.write(fila,4,res['documentos_operados'])


            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'libro_compras.xlsx'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account_gt.libro_compras.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    # def test(self):
    #     liquidacion_ids = self.env['account_gt.liquidacion'].search([('company_id','=',self.env.company.id),('name','=','Nuevo')], order="id asc")
    #     if liquidacion_ids:
    #         contador = 1
    #         for l in liquidacion_ids:
    #             logging.warn(l.id)
    #             if contador < 10:
    #                 l.write({'name': 'Liquidacion0000'+str(contador)})
    #                 contador += 1
    #             else:
    #                 l.write({'name': 'Liquidacion000'+str(contador)})
    #                 contador += 1
        # for l in factura.invoice_line_ids:
        #     l.create_analytic_lines()
        # factura.button_draft()
        # factura.action_post()
        # factura._compute_payments_widget_to_reconcile_info()
