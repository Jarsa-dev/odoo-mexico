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
from openerp.tools.translate import _
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import time
from openerp import tools
import urllib2
try:
    from qrtools import QR
except:
    pass

codigos = {
    200 : 'OK',
    301 : 'XML mal formado',
    302 : 'Sello mal formado o Invalido',
    303 : 'Sello no corresponde al emisor',
    304 : 'Certificado revocado o caduco',
    305 : 'Fecha emision no esta dentro de vigencia CSD emisor',
    306 : 'Certificado no es tipo CSD (puede ser FIEL)',
    307 : 'CFDI contiene timbre previo',
    308 : 'Certificado no expedido por SAT',
    401 : 'Fecha y hora de generacion fuera de rango (72 horas)',
    402 : 'RFC emisor no se encuentra en regimen contribuyentes',
    403 : 'Fecha emision no es posterior a 2011-01-01',
    500 : 'Error interno en el servicio.',
    700 : 'Error en autorizacion del usuario',
    701 : 'No autorizado',
    702 : 'Combinacion de usuario/contraseña invalida',
    703 : 'Saldo insuficiente',
    704 : 'Usuario distinto del RFC emisor (no aplica para usuarios de tipo agencia)',
    801 : 'Version del comprobante en la fecha de emision es invalida',
    802 : 'Version 3.0 del CFDi es obsoleta',
    803 : 'RFC no tiene validez de obligaciones para emitir CFDIs',
    901 : 'Solicitud demasiado grande',
    902 : 'Solicitud contiene caracteres ilegales',
    903 : 'Solicitud no contiene los parametros requeridos',
    904 : 'Solicitud vacia',
    905 : 'Metodo de HTTP no permitido',
    906 : 'Content-Type no permitido',
    907 : 'Encoding no permitido',
    908 : 'Content-Length no coincide con el tamano de la solicitud recibida',
    922 : 'Factura timbrada previamente',
           }


codigos_cancel = {    
    201 : 'Folio Fiscal Cancelado Exitosamente',
    202 : 'Folio Fiscal Previamente cancelado',
    203 : 'Folio Fiscal no corresponde a RFC Emisor y de quien solicita Cancelacion',
    204 : 'No aplica cancelacion',
    205 : 'Folio Fiscal no existe',
    '001' : 'Errores en la peticion al servicio - Peticion vacia',
    '002' : 'Errores en la peticion al servicio - Tamano de la peticion demasiado grande',
    '003' : 'Errores en la peticion al servicio - Peticion de http incorrecta',
    700 : 'Errores de autenticacion o autorizacion - Usuario o contrasena invalida',
    702 : 'Errores de autenticacion o autorizacion - Usuario o contrasena invalida',
    703 : 'Errores de autenticacion o autorizacion - Usuario o contrasena invalida',
    708 : 'Errores de autenticacion o autorizacion - Usuario o contrasena invalida',
    306 : 'Errores de Lista de Contribuyentes Obligados - El RFC no contiene el numero de certificado indicado en la Lista de Contribuyentes Obligados',
    402 : 'Errores de Lista de Contribuyentes Obligados - El RFC no se encuentra en la Lista de Contribuyentes Obligados',
    803 : 'Errores de Lista de Contribuyentes Obligados - El RFC no cuenta con obligaciones validas en la Lista de Contribuyentes Obligados',
    304 : 'Errores en la validacion del sello o CSD - Certificado Caduco o con Error',
    302 : 'Errores en la validacion del sello o CSD - Sello invalido',
    303 : 'Errores en la validacion del sello o CSD - El certificado no pertenece al emisor',
    305 : 'Errores en la validacion del sello o CSD - Fecha de emision de la cancelacion fuera de la fecha de validez del certificado',
    306 : 'Errores en la validacion del sello o CSD - Certificado no es CSD',
    308 : 'Errores en la validacion del sello o CSD - Certificado no expedido por el SAT',
    900 : 'Errores en el servicio de cancelacion del SAT - Servicio de cancelacion del SAT no disponible (intentar mas tarde)',
    945 : 'Errores en el servicio de cancelacion del SAT - Servicio de cancelacion del SAT no disponible (intentar mas tarde)',
    946 : 'Errores en el servicio de cancelacion del SAT - Servicio de cancelacion del SAT no disponible (intentar mas tarde)',
    949 : 'Errores en el servicio de cancelacion del SAT - Respuesta incompleta del servicio de cancelacion del SAT (se recomienda reintentar)',
    950 : 'Errores en el servicio de cancelacion del SAT - Respuesta incompleta del servicio de cancelacion del SAT (se recomienda reintentar)',
    332 : 'Errores en el servicio de cancelacion de Comercio Digtial (Errores internos) - Error Interno en el servicio de Cancelacion',
    333 : 'Errores en el servicio de cancelacion de Comercio Digtial (Errores internos) - Error Interno en el servicio de Cancelacion',
    334 : 'Errores en el servicio de cancelacion de Comercio Digtial (Errores internos) - Error Interno en el servicio de Cancelacion',
    400 : 'Otro error, ver la respuesta.',
    910 : 'Errores en el servicio de cancelacion de Comercio Digtial (Errores internos) - Error Interno en el servicio de Cancelacion',
    951 : 'Errores en el servicio de cancelacion de Comercio Digtial (Errores internos) - Error Interno en el servicio de Cancelacion',
        }

class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        types = super(ir_attachment_facturae_mx, self)._get_type(
            cr, uid, ids, context=context)
        types.extend([
            ('cfdi32_pac_cd', 'CFDI 3.2 Comercio Digital'),
        ])
        return types
    
    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_cd': self._upload_ws_file})
        return factura_mx_type__fc
    
    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_cd': self.cd_cancel})
        return factura_mx_type__fc
        
    _columns = {
        'type': fields.selection(_get_type, 'Type', type='char', size=64,
                                 required=True, readonly=True, help="Type of Electronic Invoice"),
    }

    
    def cd_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        msg = ''
        certificate_obj = self.pool.get('res.company.facturae.certificate')
        pac_params_obj = self.pool.get('params.pac')
        invoice_obj = self.pool.get('account.invoice')
        for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
            status = False
            invoice = ir_attachment_facturae_mx_id.invoice_id
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'pac_cd_cancelar'),
                ('company_id', '=', invoice.company_emitter_id.id),
                ('active', '=', True),
            ], limit=1, context=context)
            pac_params_id = pac_params_ids and pac_params_ids[0] or False            
            
            if pac_params_id:
                file_globals = invoice_obj._get_file_globals(cr, uid, [invoice.id], context=context)
                fname_cer_no_pem = file_globals['fname_cer_no_pem']
                #cerCSD = fname_cer_no_pem and base64.encodestring(open(fname_cer_no_pem, "r").read()) or ''
                cerCSD = fname_cer_no_pem and base64.b64encode(open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = file_globals['fname_key_no_pem']
                #keyCSD = fname_key_no_pem and base64.encodestring(open(fname_key_no_pem, "r").read()) or ''
                keyCSD = fname_key_no_pem and base64.b64encode(open(fname_key_no_pem, "r").read()) or ''
                pac_params_brw = pac_params_obj.browse(cr, uid, [pac_params_id], context=context)[0]
                user = pac_params_brw.user
                password = pac_params_brw.password
                wsdl_url = pac_params_brw.url_webservice
                
                http = urllib2.build_opener(urllib2.ProxyHandler, urllib2.UnknownHandler, urllib2.HTTPHandler, urllib2.HTTPDefaultErrorHandler, urllib2.FTPHandler, urllib2.FileHandler, urllib2.HTTPErrorProcessor)
                data = "RFC ={0}\nUSER={1}\nPWDW={2}\nUUID={3}\nCERT={4}\nKEYF={5}\nPWDK={6}\nACUS=SI".format(user,user,password,invoice.cfdi_folio_fiscal,cerCSD,keyCSD,invoice.company_emitter_id.certificate_id.certificate_password)
                req = urllib2.Request(url=wsdl_url, data=data, headers={'Content-Type': 'text/plain'})

                try:
                    response = http.open(req)
                    response_text = response.read()
                    try:	
                        xml = minidom.parseString(response_text)
                        estatusUUID = xml.documentElement.getElementsByTagName("EstatusUUID")[0].firstChild.nodeValue
                        uuid = xml.documentElement.getElementsByTagName("UUID")[0].firstChild.nodeValue		
                        codigo = int(estatusUUID)
                        respuesta = response_text
                    except Exception, e:
                        codigo = 400
                        respuesta = response_text                    
                except urllib2.HTTPError, e:
                    codigo = 500
                    respuesta = "Error interno en el servicio de Cancelacion. Por favor intente de nuevo."
                    
                if codigo == 201:
                    msg +=  respuesta + _('\n- The process of cancellation has completed correctly.\n- The uuid cancelled is: ') + uuid
                    invoice_obj.write(cr, uid, [invoice.id], {
                        'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'cfdi_folio_fiscal_cancel' : uuid,
                    })
                    status = True
                else:
                    msg += "\nOcurrio un error.\nCodigo: %s\nRespuesta: %s" % (codigo, codigos_cancel[codigo])
                    #print "msg: ", msg
                    status = False
                    #raise osv.except_osv(_('Warning'), _('There was something wrong processing CFDI file...'))
            else:
                msg = _('Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        return {'message': msg, 'status_uuid': True, 'status': status}
    
    def _upload_ws_file(self, cr, uid, ids, fdata=None, context=None):
        """
        @params fdata : File.xml codification in base64
        """
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        pac_params_obj = invoice_obj.pool.get('params.pac')
        for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
            invoice = ir_attachment_facturae_mx_id.invoice_id
            comprobante = invoice_obj._get_type_sequence(cr, uid, [invoice.id], context=context)
            cfd_data = base64.decodestring(fdata or invoice_obj.fdata)
            xml_res_str = xml.dom.minidom.parseString(cfd_data)
            xml_res_addenda = xml_res_str
            
            if tools.config['test_report_directory']:#TODO: Add if test-enabled:
                ir_attach_facturae_mx_file_input = ir_attachment_facturae_mx_id.file_input and ir_attachment_facturae_mx_id.file_input or False
                fname_suffix = ir_attach_facturae_mx_file_input and ir_attach_facturae_mx_file_input.datas_fname or ''
                open( os.path.join(tools.config['test_report_directory'], 'l10n_mx_facturae_pac_cd' + '_' + \
                  'before_upload' + '-' + fname_suffix), 'wb+').write( xml_res_str_addenda )
            compr = xml_res_addenda.getElementsByTagName(comprobante)[0]
            date = compr.attributes['fecha'].value
            date_format = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
            context['date'] = date_format
            invoice_ids = [invoice.id]
            file = False
            msg = ''
            cfdi_xml = False
            pac_params_ids = pac_params_obj.search(cr, uid, [('method_type', '=', 'pac_cd_firmar'), 
                                                             ('company_id', '=', invoice.company_emitter_id.id), 
                                                             ('active', '=', True)], limit=1, context=context)
            if pac_params_ids:
                pac_params = pac_params_obj.browse(cr, uid, pac_params_ids, context)[0]
                user = pac_params.user
                password = pac_params.password
                wsdl_url = pac_params.url_webservice + "?rfc={0}&pwd={1}".format(user,password)

                if not (pac_params.url_webservice):
                    raise osv.except_osv(_('Warning'), _('Web Service URL o PAC incorrect'))

                if 'pruebas' in wsdl_url:
                    msg += _(u'WARNING, SIGNED IN TEST!!!!\n\n')
                
                http = urllib2.build_opener(urllib2.ProxyHandler, urllib2.UnknownHandler, urllib2.HTTPHandler,urllib2.HTTPDefaultErrorHandler, urllib2.FTPHandler, urllib2.FileHandler, urllib2.HTTPErrorProcessor)
                req = urllib2.Request(url=wsdl_url, data='%s' % (cfd_data.replace(chr(239), "").replace(chr(187), "").replace(chr(191), "").replace("\n", "")), headers={'Content-Type': 'text/xml'})
                #print "cfd_data: '%s'" % (cfd_data[3:])
                try:
                    response = http.open(req)
                    codigo = response.code
                    respuesta = response.read()
                except urllib2.HTTPError, e:
                    codigo = e.code
                    respuesta = e.read()

                if codigo==200:
                    htz=int(invoice_obj._get_time_zone(cr, uid, [ir_attachment_facturae_mx_id.invoice_id.id], context=context))
                    dom_respuesta = minidom.parseString(respuesta)
                    timbre = dom_respuesta.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
                    if not timbre.attributes['UUID'].value:
                        msg += "\nEl timbrado no fue realizado correctamente ya que no regreso el UUID..."
                        
                    date = timbre.attributes['FechaTimbrado'].value
                    
                    fecha_timbrado = timbre.attributes['FechaTimbrado'].value or False
                    fecha_timbrado = fecha_timbrado and time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                    fecha_timbrado = fecha_timbrado and datetime.strptime(fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False
                    original =  ("</cfdi:Impuestos>").encode('utf8')
                    replacement = ("</cfdi:Impuestos><cfdi:Complemento>" + respuesta + "</cfdi:Complemento>").encode('utf8')
                                        
                    qr_bytes = self.create_qr_image(cr, uid, ids, cfd_data, invoice, timbre.attributes['UUID'].value)
                    
                    cfdi_data = {
                        'cfdi_cbb'              : qr_bytes,  # a lo regresa en base64
                        'cfdi_sello'            : timbre.attributes['selloSAT'].value or False,
                        'cfdi_no_certificado'   : timbre.attributes['noCertificadoSAT'].value or False,
                        #'cfdi_cadena_original'  : False,
                        'cfdi_fecha_timbrado'   : fecha_timbrado,
                        'cfdi_xml'              : cfd_data.replace(original, replacement) or '',  # este se necesita en uno que no es base64
                        'cfdi_folio_fiscal'     : timbre.attributes['UUID'].value or '',
                        'pac_id'                : pac_params.id,
                    }
                    
                    msg += "\nFolio Fiscal: " + timbre.attributes['UUID'].value
                    msg += 'Puede validar el archivo generado en el SAT en\n https://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html'
                    if cfdi_data.get('cfdi_xml', False):
                        url_pac = '</"%s"><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://solucionfactible.com/cfdi/00001000000102699425.zip-->' % (comprobante)
                        cfdi_data['cfdi_xml'] = cfdi_data['cfdi_xml'].replace('</"%s">' % (comprobante), url_pac)
                        file = base64.encodestring(cfdi_data['cfdi_xml'] or '')
                        # invoice_obj.cfdi_data_write(cr, uid, [invoice.id], cfdi_data, context=context)
                        cfdi_xml = cfdi_data.pop('cfdi_xml')
                        if cfdi_xml:
                            invoice_obj.write(cr, uid, [invoice.id], cfdi_data)
                            cfdi_data['cfdi_xml'] = cfdi_xml
                        else:
                            msg += _(u"Can't extract the file XML of PAC")
                                        
                else:
                    msg += "\nOcurrio un error.\nCodigo: %s\nRespuesta: %s" % (codigo, codigos[codigo])
                    #raise osv.except_osv(_('Warning'), _('There was something wrong processing CFDI file...\nCode: %s\nDescription: %s')%(codigo, codigos[codigo]))
            else:
                msg += 'Not found information from web services of PAC, verify that the configuration of PAC is correct'
                #raise osv.except_osv(_('Warning'), _(
                #    'Not found information from web services of PAC, verify that the configuration of PAC is correct'))
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml}

        
    def create_qr_image(self, cr, uid, ids, cfdi_xml, invoice, timbre_uuid, context=None):
        #Get info for QRC
        cfdi_minidom = minidom.parseString(cfdi_xml)
        
        node = cfdi_minidom.getElementsByTagName('cfdi:Comprobante')[0]
        subnode = node.getElementsByTagName('cfdi:Emisor')[0]
        qr_emisor = subnode.getAttribute('rfc')        
        subnode = node.getElementsByTagName('cfdi:Receptor')[0]        
        qr_receptor = subnode.getAttribute('rfc')
        total = "%017f"%( invoice.amount_total or 0.0)
        qr_total = total        
        qr_string = '?re=%s&rr=%s&tt=%s&id=%s'%(qr_emisor, qr_receptor, total, timbre_uuid)
        qr_code = QR(data=qr_string.encode('utf-8'))
        try:
            qr_code.encode()
        except Exception, e:
            raise osv.except_osv(_('Warning'), _('Could not create QR Code image.\nError %s') % e)            
        if qr_code.filename is None:
            pass
        else:
            qr_file = open(qr_code.filename, "rb")
            temp_bytes = qr_file.read()
            qr_bytes = base64.encodestring(temp_bytes)
            qr_file.close()
            
        return qr_bytes or False


        
# vim:expandtab:smartinde
