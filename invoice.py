# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Israel Cruz Argil (israel.cruz@hesatecnica.com
############################################################################
#    Coded by: Israel Cruz Argil (israel.cruz@hesatecnica.com
#    Financed by: http://www.transportesmar.com.mx/ Jesús Alan Ramos Rodríguez <alan.ramos@transportesmar.com.mx>
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
from openerp import tools
from openerp import netsvc
from openerp.tools.misc import ustr
import wizard
import base64
import xml.dom.minidom
import time
import StringIO
import csv
import tempfile
import os
import sys
import codecs
from xml.dom import minidom
import urllib
import pooler
from tools.translate import _
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import time
from datetime import datetime, timedelta
import time


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    _columns = {
        'cfdi_cbb': fields.binary('CFD-I CBB'),
        'cfdi_sello': fields.text('CFD-I Sello', help='Sign assigned by the SAT'),
        'cfdi_no_certificado': fields.char('CFD-I Certificado', size=32,
                                           help='Serial Number of the Certificate'),
        'cfdi_cadena_original': fields.text('CFD-I Cadena Original',
                                            help='Original String used in the electronic invoice'),
        'cfdi_fecha_timbrado': fields.datetime('CFD-I Fecha Timbrado',
                                               help='Date when is stamped the electronic invoice'),
        'cfdi_fecha_cancelacion': fields.datetime('CFD-I Fecha Cancelacion',
                                                  help='If the invoice is cancel, this field saved the date when is cancel'),
        'cfdi_folio_fiscal': fields.char('CFD-I Folio Fiscal', size=64,
                                         help='UUID del Timbrado de Factura'),
        'cfdi_folio_fiscal_cancel': fields.char('CFD-I Folio Fiscal Cancelacion', size=64,
                                         help='UUID de Cancelación de Timbre de Factura'),
    }

    def cfdi_data_write(self, cr, uid, ids, cfdi_data, context=None):
        """
        @params cfdi_data : * TODO
        """
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        attachment_obj = self.pool.get('ir.attachment')
        cfdi_xml = cfdi_data.pop('cfdi_xml')
        if cfdi_xml:
            self.write(cr, uid, ids, cfdi_data)
            cfdi_data['cfdi_xml'] = cfdi_xml  # Regresando valor, despues de hacer el write normal
            """for invoice in self.browse(cr, uid, ids):
                #fname, xml_data = self.pool.get('account.invoice').\
                    _get_facturae_invoice_xml_data(cr, uid, [inv.id],
                    context=context)
                fname_invoice = invoice.fname_invoice and invoice.\
                    fname_invoice + '.xml' or ''
                data_attach = {
                    'name': fname_invoice,
                    'datas': base64.encodestring( cfdi_xml or '') or False,
                    'datas_fname': fname_invoice,
                    'description': 'Factura-E XML CFD-I',
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }
                attachment_ids = attachment_obj.search(cr, uid, [('name','=',\
                    fname_invoice),('res_model','=','account.invoice'),(
                    'res_id', '=', invoice.id)])
                if attachment_ids:
                    attachment_obj.write(cr, uid, attachment_ids, data_attach,
                        context=context)
                else:
                    attachment_obj.create(cr, uid, data_attach, context=context)
                """
        return True

    def copy(self, cr, uid, id, default={}, context=None):
        if context is None:
            context = {}
        default.update({
            'cfdi_cbb': False,
            'cfdi_sello': False,
            'cfdi_no_certificado': False,
            'cfdi_cadena_original': False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
            'cfdi_fecha_cancelacion': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)
    """
    TODO: reset to draft considerated to delete these fields?
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'cfdi_cbb': False,
            'cfdi_sello':False,
            'cfdi_no_certificado':False,
            'cfdi_cadena_original':False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
            'cfdi_fecha_cancelacion': False,
        })
        return super(account_invoice, self).action_cancel_draft(cr, uid, ids, args)
    """

    def _get_file(self, cr, uid, inv_ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        invoice = self.browse(cr, uid, ids, context=context)[0]
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
            '.xml' or ''
        aids = self.pool.get('ir.attachment').search(cr, uid, [(
            'datas_fname', '=', invoice.fname_invoice+'.xml'), (
                'res_model', '=', 'account.invoice'), ('res_id', '=', id)])
        xml_data = ""
        if aids:
            brow_rec = self.pool.get('ir.attachment').browse(cr, uid, aids[0])
            if brow_rec.datas:
                xml_data = base64.decodestring(brow_rec.datas)
        else:
            fname, xml_data = self._get_facturae_invoice_xml_data(
                cr, uid, inv_ids, context=context)
            self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
            }, context=None)#Context, because use a variable type of our code but we dont need it.
        self.fdata = base64.encodestring(xml_data)
        msg = _("Press in the button  'Upload File'")
        return {'file': self.fdata, 'fname': fname_invoice,
                'name': fname_invoice, 'msg': msg}

#    def add_node(self, node_name=None, attrs=None, parent_node=None,
#                 minidom_xml_obj=None, attrs_types=None, order=False):
#        """
#            @params node_name : Name node to added
#            @params attrs : Attributes to add in node
#            @params parent_node : Node parent where was add new node children
#            @params minidom_xml_obj : File XML where add nodes
#            @params attrs_types : Type of attributes added in the node
#            @params order : If need add the params in order in the XML, add a
#                    list with order to params
#        """
#        if not order:
#            order = attrs
#        new_node = minidom_xml_obj.createElement(node_name)
#        for key in order:
#            if attrs_types[key] == 'attribute':
#                new_node.setAttribute(key, attrs[key])
#            elif attrs_types[key] == 'textNode':
#                key_node = minidom_xml_obj.createElement(key)
#                text_node = minidom_xml_obj.createTextNode(attrs[key])
#
#                key_node.appendChild(text_node)
#                new_node.appendChild(key_node)
#        parent_node.appendChild(new_node)
#        return new_node

#    def add_addenta_xml(self, cr, ids, xml_res_str=None, comprobante=None, context=None):
#        """
#         @params xml_res_str : File XML
#         @params comprobante : Name to the Node that contain the information the XML
#        """
#        if context is None:
#            context = {}
#        if xml_res_str:
#            node_Addenda = xml_res_str.getElementsByTagName('cfdi:Addenda')
#            if len(node_Addenda) == 0:
#                nodeComprobante = xml_res_str.getElementsByTagName(
#                    comprobante)[0]
#                node_Addenda = self.add_node(
#                    'cfdi:Addenda', {}, nodeComprobante, xml_res_str, attrs_types={})
#                node_Partner_attrs = {
#                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
#                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
#                    'id': "150731"
#                }
#                node_Partner_attrs_types = {
#                    'xmlns:sf': 'attribute',
#                    'xsi:schemaLocation': 'attribute',
#                    'id': 'attribute'
#                }
#                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
#                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
#            else:
#                node_Partner_attrs = {
#                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
#                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
#                    'id': "150731"
#                }
#                node_Partner_attrs_types = {
#                    'xmlns:sf': 'attribute',
#                    'xsi:schemaLocation': 'attribute',
#                    'id': 'attribute'
#                }
#                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
#                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
#        return xml_res_str

    def _get_type_sequence(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [(
            'sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(
                cr, uid, sequence_app_id[0], context=context).type
        if 'cfdi' in type_inv:
            comprobante = 'cfdi:Comprobante'
        else:
            comprobante = 'Comprobante'
        return comprobante

    def _get_time_zone(self, cr, uid, invoice_id, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        userstz = res_users_obj.browse(cr, uid, [uid])[0].partner_id.tz
        a = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.now(pytz.timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s)*-1
            a = timezone_original + ((
                timezone_present + timezone_original)*-1)
        return a
    
    def _get_file_cancel(self, cr, uid, inv_ids, context=None):
        if context is None:
            context = {}
        inv_ids = inv_ids[0]
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.search(cr, uid, [('res_id', '=', inv_ids), (
            'name', 'ilike', '%.xml')], context=context)
        res = {}
        if atta_id:
            atta_brw = atta_obj.browse(cr, uid, atta_id, context)[0]
            inv_xml = atta_brw.datas or False
        else:
            inv_xml = False
            raise osv.except_osv(('State of Cancellation!'), (
                "This invoice hasn't stamped, so that not possible cancel."))
        return {'file': inv_xml}

    def write_cfd_data(self, cr, uid, ids, cfd_datas, context=None):
        """
        @param cfd_datas : Dictionary with data that is used in facturae CFDI
        """
        if context is None:
            context = {}
        if not cfd_datas:
            cfd_datas = {}
        comprobante = self._get_type_sequence(cr, uid, ids, context=context)
        # obtener cfd_data con varios ids
        # for id in ids:
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if True:
            data = {}
            cfd_data = cfd_datas
            noCertificado = cfd_data.get(
                comprobante, {}).get('noCertificado', '')
            certificado = cfd_data.get(comprobante, {}).get('certificado', '')
            sello = cfd_data.get(comprobante, {}).get('sello', '')
            cadena_original = cfd_data.get('cadena_original', '')
            data = {
                'no_certificado': noCertificado,
                'certificado': certificado,
                'sello': sello,
                'cadena_original': cadena_original,
            }
            self.write(cr, uid, ids, data, context=context)
        return True

    
    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoices = self.browse(cr, uid, ids, context=context)
        invoice_tax_obj = self.pool.get("account.invoice.tax")
        invoice_datas = []
        invoice_data_parents = []
        #'type': fields.selection([
            #('out_invoice','Customer Invoice'),
            #('in_invoice','Supplier Invoice'),
            #('out_refund','Customer Refund'),
            #('in_refund','Supplier Refund'),
            #],'Type', readonly=True, select=True),
        for invoice in invoices:
            invoice_data_parent = {}
            if invoice.type == 'out_invoice':
                tipoComprobante = 'ingreso'
            elif invoice.type == 'out_refund':
                tipoComprobante = 'egreso'
            else:
                raise osv.except_osv(_('Warning !'), _(
                    'Only can issue electronic invoice to customers.!'))
            # Inicia seccion: Comprobante
            invoice_data_parent['Comprobante'] = {}
            # default data
            invoice_data_parent['Comprobante'].update({
                'xmlns': "http://www.sat.gob.mx/cfd/2",
                'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/2 http://www.\
                sat.gob.mx/sitio_internet/cfd/2/cfdv2.xsd",
                'version': "2.0",
            })
            number_work = invoice.number or invoice.internal_number
            invoice_data_parent['Comprobante'].update({
                'folio': number_work,
                'fecha': invoice.date_invoice_tz and
                # time.strftime('%d/%m/%y',
                # time.strptime(invoice.date_invoice, '%Y-%m-%d'))
                time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(
                invoice.date_invoice_tz, '%Y-%m-%d %H:%M:%S'))
                or '',
                'tipoDeComprobante': tipoComprobante,
                'formaDePago': u'Pago en una sola exhibición',
                'noCertificado': '@',
                'sello': '@',
                'certificado': '@',
                'subTotal': "%.2f" % (invoice.amount_untaxed or 0.0),
                'descuento': "0",  # Add field general
                'total': "%.2f" % (invoice.amount_total or 0.0),
            })
            folio_data = self._get_folio(
                cr, uid, [invoice.id], context=context)
            invoice_data_parent['Comprobante'].update({
                'anoAprobacion': folio_data['anoAprobacion'],
                'noAprobacion': folio_data['noAprobacion'],
            })
            serie = folio_data.get('serie', False)
            if serie:
                invoice_data_parent['Comprobante'].update({
                    'serie': serie,
                })
            # Termina seccion: Comprobante
            # Inicia seccion: Emisor
            partner_obj = self.pool.get('res.partner')
            address_invoice = invoice.address_issued_id or False
            address_invoice_parent = invoice.company_emitter_id and \
            invoice.company_emitter_id.address_invoice_parent_company_id or False

            if not address_invoice:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined the address issuing!"))

            if not address_invoice_parent:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined an address of invoicing from the company!"))

            if not address_invoice_parent.vat:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined RFC for the address of invoice to the company!"))

            invoice_data = invoice_data_parent['Comprobante']
            invoice_data['Emisor'] = {}
            invoice_data['Emisor'].update({

                'rfc': (('vat_split' in address_invoice_parent._columns and \
                address_invoice_parent.vat_split or address_invoice_parent.vat) \
                or '').replace('-', ' ').replace(' ', '').upper(),
                'nombre': address_invoice_parent.name or '',
                # Obtener domicilio dinamicamente
                # virtual_invoice.append( (invoice.company_id and
                # invoice.company_id.partner_id and
                # invoice.company_id.partner_id.vat or '').replac

                'DomicilioFiscal': {
                    'calle': address_invoice_parent.street and \
                        address_invoice_parent.street.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or '',
                    'noExterior': address_invoice_parent.l10n_mx_street3 and \
                        address_invoice_parent.l10n_mx_street3.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or 'N/A',  # "Numero Exterior"
                    'noInterior': address_invoice_parent.l10n_mx_street4 and \
                        address_invoice_parent.l10n_mx_street4.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or 'N/A',  # "Numero Interior"
                    'colonia':  address_invoice_parent.street2 and \
                        address_invoice_parent.street2.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or False,
                    'localidad': address_invoice_parent.l10n_mx_city2 and \
                        address_invoice_parent.l10n_mx_city2.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or False,
                    'municipio': address_invoice_parent.city and \
                        address_invoice_parent.city.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or '',
                    'estado': address_invoice_parent.state_id and \
                        address_invoice_parent.state_id.name and \
                        address_invoice_parent.state_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'pais': address_invoice_parent.country_id and \
                        address_invoice_parent.country_id.name and \
                        address_invoice_parent.country_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice_parent.zip and \
                        address_invoice_parent.zip.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ').replace(' ', '') or '',
                },
                'ExpedidoEn': {
                    'calle': address_invoice.street and address_invoice.\
                        street.replace('\n\r', ' ').replace('\r\n', ' ').\
                        replace('\n', ' ').replace('\r', ' ') or '',
                    'noExterior': address_invoice.l10n_mx_street3 and \
                        address_invoice.l10n_mx_street3.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or 'N/A',  # "Numero Exterior"
                    'noInterior': address_invoice.l10n_mx_street4 and \
                        address_invoice.l10n_mx_street4.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or 'N/A',  # "Numero Interior"
                    'colonia':  address_invoice.street2 and address_invoice.\
                        street2.replace('\n\r', ' ').replace('\r\n', ' ').\
                        replace('\n', ' ').replace('\r', ' ') or False,
                    'localidad': address_invoice.l10n_mx_city2 and \
                        address_invoice.l10n_mx_city2.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or False,
                    'municipio': address_invoice.city and address_invoice.\
                        city.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'estado': address_invoice.state_id and address_invoice.\
                        state_id.name and address_invoice.state_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or '',
                    'pais': address_invoice.country_id and address_invoice.\
                        country_id.name and address_invoice.country_id.name.\
                        replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice.zip and address_invoice.\
                        zip.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ').replace(' ', '') or '',
                },
            })
            if invoice_data['Emisor']['DomicilioFiscal'].get('colonia') == False:
                invoice_data['Emisor']['DomicilioFiscal'].pop('colonia')
            if invoice_data['Emisor']['ExpedidoEn'].get('colonia') == False:
                invoice_data['Emisor']['ExpedidoEn'].pop('colonia')
            if invoice_data['Emisor']['DomicilioFiscal'].get('localidad') == False:
                invoice_data['Emisor']['DomicilioFiscal'].pop('localidad')
            if invoice_data['Emisor']['ExpedidoEn'].get('localidad') == False:
                invoice_data['Emisor']['ExpedidoEn'].pop('localidad')
            # Termina seccion: Emisor
            # Inicia seccion: Receptor
            parent_id = invoice.partner_id.commercial_partner_id.id
            parent_obj = partner_obj.browse(cr, uid, parent_id, context=context)
            if not parent_obj.vat:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined RFC of the partner[%s].\n%s !") % (
                    parent_obj.name, msg2))
            if parent_obj._columns.has_key('vat_split') and parent_obj.vat[0:2].upper() <> 'MX':
                    rfc = 'XAXX010101000'
            else:
                rfc = ((parent_obj._columns.has_key('vat_split')\
                    and parent_obj.vat_split or parent_obj.vat)\
                    or '').replace('-', ' ').replace(' ','').upper()
            address_invoice = partner_obj.browse(cr, uid, \
                invoice.partner_id.id, context=context)
            invoice_data['Receptor'] = {}
            invoice_data['Receptor'].update({
                'rfc': rfc.upper(),
                'nombre': (parent_obj.name or ''),
                'Domicilio': {
                    'calle': address_invoice.street and address_invoice.\
                        street.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'noExterior': address_invoice.l10n_mx_street3 and \
                        address_invoice.l10n_mx_street3.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or 'N/A',  # "Numero Exterior"
                    'noInterior': address_invoice.l10n_mx_street4 and \
                        address_invoice.l10n_mx_street4.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or 'N/A',  # "Numero Interior"
                    'colonia':  address_invoice.street2 and address_invoice.\
                        street2.replace('\n\r', ' ').replace('\r\n', ' ').\
                        replace('\n', ' ').replace('\r', ' ') or False,
                    'localidad': address_invoice.l10n_mx_city2 and \
                        address_invoice.l10n_mx_city2.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or False,
                    'municipio': address_invoice.city and address_invoice.\
                        city.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'estado': address_invoice.state_id and address_invoice.\
                        state_id.name and address_invoice.state_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or '',
                    'pais': address_invoice.country_id and address_invoice.\
                        country_id.name and address_invoice.country_id.name.\
                        replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice.zip and address_invoice.\
                        zip.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                },
            })
            if invoice_data['Receptor']['Domicilio'].get('colonia') == False:
                invoice_data['Receptor']['Domicilio'].pop('colonia')
            if invoice_data['Receptor']['Domicilio'].get('localidad') == False:
                invoice_data['Receptor']['Domicilio'].pop('localidad')
            # Termina seccion: Receptor
            # Inicia seccion: Conceptos
            invoice_data['Conceptos'] = []
            for line in invoice.invoice_line:
                # price_type = invoice._columns.has_key('price_type') and invoice.price_type or 'tax_excluded'
                # if price_type == 'tax_included':
# price_unit = line.price_subtotal/line.quantity#Agrega compatibilidad con
# modulo TaxIncluded
                price_unit = line.quantity != 0 and line.price_subtotal / \
                    line.quantity or 0.0
                concepto = {
                    'cantidad': "%.2f" % (line.quantity or 0.0),
                    'descripcion': line.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                    'valorUnitario': "%.2f" % (price_unit or 0.0),
                    'importe': "%.2f" % (line.price_subtotal or 0.0),  # round(line.price_unit *(1-(line.discount/100)),2) or 0.00),#Calc: iva, disc, qty
                    # Falta agregar discount
                }
                unidad = line.uos_id and line.uos_id.name or ''
                if unidad:
                    concepto.update({'unidad': unidad})
                product_code = line.product_id and line.product_id.default_code or ''
                if product_code:
                    concepto.update({'noIdentificacion': product_code})
                invoice_data['Conceptos'].append({'Concepto': concepto})

                pedimento = None
                if 'tracking_id' in line._columns:
                    pedimento = line.tracking_id and line.tracking_id.import_id or False
                    if pedimento:
                        informacion_aduanera = {
                            'numero': pedimento.name or '',
                            'fecha': pedimento.date or '',
                            'aduana': pedimento.customs,
                        }
                        concepto.update({
                                        'InformacionAduanera': informacion_aduanera})
                # Termina seccion: Conceptos
            # Inicia seccion: impuestos
            invoice_data['Impuestos'] = {}
            invoice_data['Impuestos'].update({
                #'totalImpuestosTrasladados': "%.2f"%( invoice.amount_tax or 0.0),
            })
            invoice_data['Impuestos'].update({
                #'totalImpuestosRetenidos': "%.2f"%( invoice.amount_tax or 0.0 )
            })

            invoice_data_impuestos = invoice_data['Impuestos']
            invoice_data_impuestos['Traslados'] = []
            # invoice_data_impuestos['Retenciones'] = []

            tax_names = []
            totalImpuestosTrasladados = 0
            totalImpuestosRetenidos = 0
            for line_tax_id in invoice.tax_line:
                tax_name = line_tax_id.name2
                tax_names.append(tax_name)
                line_tax_id_amount = abs(line_tax_id.amount or 0.0)
                if line_tax_id.amount >= 0:
                    impuesto_list = invoice_data_impuestos['Traslados']
                    impuesto_str = 'Traslado'
                    totalImpuestosTrasladados += line_tax_id_amount
                else:
                    # impuesto_list = invoice_data_impuestos['Retenciones']
                    impuesto_list = invoice_data_impuestos.setdefault(
                        'Retenciones', [])
                    impuesto_str = 'Retencion'
                    totalImpuestosRetenidos += line_tax_id_amount
                    invoice_data['Impuestos'].update({
                                    'totalImpuestosRetenidos': "%.2f" % (totalImpuestosRetenidos)
                                    })
                impuesto_dict = {impuesto_str:
                                {
                                 'impuesto': tax_name,
                                 'importe': "%.2f" % (line_tax_id_amount),
                                 }
                                 }
                if line_tax_id.amount >= 0:
                    impuesto_dict[impuesto_str].update({
                            'tasa': "%.2f" % (abs(line_tax_id.tax_percent))})
                impuesto_list.append(impuesto_dict)
            invoice_data['Impuestos'].update({
                'totalImpuestosTrasladados': "%.2f" % (totalImpuestosTrasladados),
            })
            tax_requireds = ['IVA', 'IEPS']
            for tax_required in tax_requireds:
                if tax_required in tax_names:
                    continue
                invoice_data_impuestos['Traslados'].append({'Traslado': {
                    'impuesto': tax_required,
                    'tasa': "%.2f" % (0.0),
                    'importe': "%.2f" % (0.0),
                }})
            # Termina seccion: impuestos
            invoice_data_parents.append(invoice_data_parent)
            invoice_data_parent['state'] = invoice.state
            invoice_data_parent['invoice_id'] = invoice.id
            invoice_data_parent['type'] = invoice.type
            invoice_data_parent['invoice_datetime'] = invoice.invoice_datetime
            invoice_data_parent['date_invoice_tz'] = invoice.date_invoice_tz
            invoice_data_parent['currency_id'] = invoice.currency_id.id

            date_ctx = {'date': invoice.date_invoice_tz and time.strftime(
                '%Y-%m-%d', time.strptime(invoice.date_invoice_tz,
                '%Y-%m-%d %H:%M:%S')) or False}
            # rate = self.pool.get('res.currency').compute(cr, uid, invoice.currency_id.id, invoice.company_id.currency_id.id, 1, round=False, context=date_ctx, account=None, account_invert=False)
            # rate = 1.0/self.pool.get('res.currency')._current_rate(cr, uid,
            # [invoice.currency_id.id], name=False, arg=[],
            # context=date_ctx)[invoice.currency_id.id]
            currency = self.pool.get('res.currency').browse(
                cr, uid, [invoice.currency_id.id], context=date_ctx)[0]
            rate = currency.rate != 0 and 1.0/currency.rate or 0.0
            # print "currency.rate",currency.rate

            invoice_data_parent['rate'] = rate

        invoice_datetime = invoice_data_parents[0].get('invoice_datetime',
            {}) and datetime.strptime(invoice_data_parents[0].get(
            'invoice_datetime', {}), '%Y-%m-%d %H:%M:%S').strftime(
            '%Y-%m-%d') or False
        if not invoice_datetime:
            raise osv.except_osv(_('Date Invoice Empty'), _(
                "Can't generate a invoice without date, make sure that the state of invoice not is draft & the date of invoice not is empty"))
        if invoice_datetime < '2012-07-01':
            return invoice_data_parent
        else:
            invoice = self.browse(cr, uid, ids, context={
                                  'date': invoice_datetime})[0]
            city = invoice_data_parents and invoice_data_parents[0].get(
                'Comprobante', {}).get('Emisor', {}).get('ExpedidoEn', {}).get(
                'municipio', {}) or False
            state = invoice_data_parents and invoice_data_parents[0].get(
                'Comprobante', {}).get('Emisor', {}).get('ExpedidoEn', {}).get(
                'estado', {}) or False
            country = invoice_data_parents and invoice_data_parents[0].get(
                'Comprobante', {}).get('Emisor', {}).get('ExpedidoEn', {}).get(
                'pais', {}) or False
            if city and state and country:
                address = city + ' ' + state + ', ' + country
            else:
                raise osv.except_osv(_('Address Incomplete!'), _(
                    'Ckeck that the address of company issuing of fiscal voucher is complete (City - State - Country)'))

            if not invoice.company_emitter_id.partner_id.regimen_fiscal_id.name:
                raise osv.except_osv(_('Missing Fiscal Regime!'), _(
                    'The Fiscal Regime of the company issuing of fiscal voucher is a data required'))

            invoice_data_parents[0]['Comprobante'][
                'xsi:schemaLocation'] = 'http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv22.xsd'
            invoice_data_parents[0]['Comprobante']['version'] = '2.2'
            invoice_data_parents[0]['Comprobante'][
                'TipoCambio'] = invoice.rate or 1
            invoice_data_parents[0]['Comprobante'][
                'Moneda'] = invoice.currency_id.name or ''
            invoice_data_parents[0]['Comprobante'][
                'NumCtaPago'] = invoice.acc_payment.last_acc_number\
                    or 'No identificado'
            invoice_data_parents[0]['Comprobante'][
                'metodoDePago'] = invoice.pay_method_id.name or 'No identificado'
            invoice_data_parents[0]['Comprobante']['Emisor']['RegimenFiscal'] = {
                'Regimen': invoice.company_emitter_id.partner_id.\
                    regimen_fiscal_id.name or ''}
            invoice_data_parents[0]['Comprobante']['LugarExpedicion'] = address
        return invoice_data_parents

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    